class UnknownTagError(KeyError):
    """Raised when TagMap encounters an unknown tag"""


## Motivation
#
# TagMap handles mappings between different but related sets of tags
# used by complementary FSTs.
#
# For example, one generic wordform analysis for ‘acâhkosa’ is
# `acâhkosa+N+A+Der/Dim+N+A+Obv`. But the phrase-generation FST takes as input
# tags and definition in the form `Obv+Dim+ star`, and outputs the inflected
# phrase `little star over there`. `Obv` has the same tag name but is now a
# start tag, not an end tag, and `Der/Dim` needs to be translated to just `Dim`.
# As well, the phrase-generation FST has stricter ordering requirements on the
# input tags.
#
## Use
#
# A TagMap is initialized with a sequence of (wordform_tag, phrase_tag,
# precedence) tuples
#
# wordform_tag can be:
#   - A literal tag, e.g., "N+", which will be matched exactly
#   - A tuple of tags, e.g., ("PV/e+, "+Ind") which will be matched as a
#     subsequence
#   - DEFAULT if the phrase_tag should be used if no other mapping applies at
#     this precedence level
#
# phrase_tag can be:
#   - None if the wordform_tag is not used in the phrase transcription
#   - COPY_TAG_NAME if the characters of the wordform_tag match the
#     phrase_tag, for example: ("+Sg", COPY_TAG_NAME, x) means the same
#     thing as ("+Sg", "Sg+", x), but with less potential for copy-paste
#     mistakes.
#
# All multi-mappings are applied before single maps, and consume their tags. For
# example, a match on (("+A, "+B"), "foo", 1) will take the tags "+A" and "+B"
# out of consideration before the rules ("+A", COPY, 1) or ("+B", COPY, 1) are
# considered.
#
# The precedence number is used to sort tags before sending them to the phrase
# FST. For example, if you want Pl/Sg before Px, you could give Pl and Sg
# precedence number 1 and the possessives number 2. This precedence number is
# associated with the output tag; it is an error to give a different precedence
# value to multiple definitions that output the same tag.
class TagMap:
    DEFAULT = object()
    COPY_TAG_NAME = object()

    def __init__(self, *tag_definitions):
        """
        See the docs in crk_tag_map.py.
        """
        self._multi_mappings = []
        self._tag_mapping = {}
        self._precedences = {}
        self._defaults_by_precedence = {}

        for wordform_tag_spec, phrase_tag_spec, prec in tag_definitions:
            if isinstance(wordform_tag_spec, tuple):
                if phrase_tag_spec == TagMap.COPY_TAG_NAME:
                    raise Exception(
                        f"Error: cannot use copy with multi-tags: {wordform_tag_spec}"
                    )
                self._multi_mappings.append((wordform_tag_spec, phrase_tag_spec, prec))
            elif wordform_tag_spec == TagMap.DEFAULT:
                if prec in self._defaults_by_precedence:
                    raise Exception(
                        f"Error: multiple defaults supplied for precedence {prec}: {self._defaults_by_precedence[prec]}, {phrase_tag_spec}"
                    )
                self._defaults_by_precedence[prec] = phrase_tag_spec
            else:
                if phrase_tag_spec == TagMap.COPY_TAG_NAME:
                    assert wordform_tag_spec.startswith(
                        "+"
                    ), f"expected tag to start with + but did not: {wordform_tag_spec}"
                    phrase_tag_spec = wordform_tag_spec[1:] + "+"
                self._tag_mapping[wordform_tag_spec] = phrase_tag_spec

            if phrase_tag_spec is not None:
                if phrase_tag_spec in self._precedences:
                    if prec != self._precedences[phrase_tag_spec]:
                        raise Exception(
                            f"Error: conflicting precedences specified for {phrase_tag_spec!r}: {self._precedences[phrase_tag_spec]} and {prec}"
                        )
                else:
                    self._precedences[phrase_tag_spec] = prec

    def map_tags(self, input_tags):
        tags_for_phrase = []

        # copy input, because we may mutate it
        input_tags = input_tags[:]

        # first handle multi-mappings, which consume their matching input
        # tags so that they are not re-considered in the next steps
        for wordform_tag_spec, phrase_tag_spec, prec in self._multi_mappings:
            if is_subsequence(input_tags, wordform_tag_spec):
                if phrase_tag_spec is not None:
                    tags_for_phrase.append(phrase_tag_spec)
                input_tags = [x for x in input_tags if x not in wordform_tag_spec]

        # normal mapping
        for wordform_tag in input_tags:
            try:
                phrase_tag = self._tag_mapping[wordform_tag]
            except KeyError:
                raise UnknownTagError(wordform_tag)
            if phrase_tag is not None and phrase_tag not in tags_for_phrase:
                tags_for_phrase.append(phrase_tag)

        # if no mapping for a precedence, use default
        used_precedences = set(self._precedences[tag] for tag in tags_for_phrase)
        for prec, default in self._defaults_by_precedence.items():
            if prec not in used_precedences:
                tags_for_phrase.append(default)

        # Sort all the combined output tags generated by all previous steps
        # into precedence order
        tags_for_phrase.sort(key=self._precedences.__getitem__)

        return _flatten_tuples(tags_for_phrase)


# https://stackoverflow.com/a/52709319/14558
def is_subsequence(outer_list, target_subsequence):
    it = iter(outer_list)
    return all(x in it for x in target_subsequence)


def _flatten_tuples(l):
    ret = []
    for x in l:
        if isinstance(x, tuple):
            ret.extend(x)
        else:
            ret.append(x)
    return ret

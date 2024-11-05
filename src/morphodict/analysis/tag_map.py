class InvalidTagMapError(Exception):
    """
    Raised during TagMap.__init__ if the provided tag definitions are invalid.
    """


class MultiTagCopyError(InvalidTagMapError):
    """
    Raised when multiple tags are present but not expected
    """


class MultiplePrecedenceError(InvalidTagMapError):
    """
    Raised when a single tag has multiple precedences declared
    """


class ConflictingPrecedenceError(InvalidTagMapError):
    """
    Raised when multiple tags have the same precedence
    """


class UnknownTagError(KeyError):
    """Raised when TagMap encounters an unknown tag during processing"""


class TagMap:
    """Map between different sets of tags used by related FSTs

    # Motivation

    Sometimes different but related FSTs use similar sets of tags,
    and they might want them in specific orders.

    For example, one generic wordform analysis for ‘acâhkosa’ is
    `acâhkosa+N+A+Der/Dim+N+A+Obv`. There’s a phrase-generation FST that
    takes as input tags and definition in the form `Obv+Dim+ star`, and outputs
    the translated simple phrase `little star over there`. `Obv` has the same
    tag name but is now a start tag, not an end tag, and `Der/Dim` needs to be
    translated to just `Dim`. As well, the phrase-generation FST has stricter
    ordering requirements on the input tags.

    This class can handle all of that.

    # Use

    A TagMap is initialized with a sequence of (input_tag, output_tag,
    precedence) tuples

    input_tag can be:
      - A literal tag, e.g., "N+", which will be matched exactly
      - A tuple of tags, e.g., ("PV/e+, "+Ind") which will be matched as a
        subsequence
      - DEFAULT if this output_tag should be used if no other mapping
      applies at this precedence level

    output_tag can be:
      - None if the input_tag should be dropped
      - COPY_TAG_NAME if the characters of the input_tag match the
        output_tag, for example: ("+Sg", COPY_TAG_NAME, x) means the same
        thing as ("+Sg", "Sg+", x), but with less potential for copy-paste
        mistakes.

    All multi-mappings are applied before single maps, and consume their
    tags. For example, a match on (("+A, "+B"), "foo", 1) will take the
    tags "+A" and "+B" out of consideration before the rules ("+A",
    COPY_TAG_NAME, 1) or ("+B", COPY_TAG_NAME, 1) are considered.

    The precedence number is used to sort tags in the output list. For
    example, if you want Pl/Sg before Px, you could give Pl and Sg
    precedence number 1 and the possessives number 2. This precedence
    number is associated with the output tag; it is an error to give a
    different precedence value to multiple definitions that output the same
    tag."""

    DEFAULT = object()
    COPY_TAG_NAME = object()

    def __init__(self, *tag_definitions):
        """
        See the docs in source_tag_map.py.
        """
        self._multi_mappings = []
        self._tag_mapping = {}
        self._precedences = {}
        self._defaults_by_precedence = {}

        for input_tag_spec, output_tag_spec, prec in tag_definitions:
            if isinstance(input_tag_spec, tuple):
                if output_tag_spec == TagMap.COPY_TAG_NAME:
                    raise MultiTagCopyError(
                        f"Error: cannot use copy with multi-tags: {input_tag_spec}"
                    )
                self._multi_mappings.append((input_tag_spec, output_tag_spec, prec))
            elif input_tag_spec == TagMap.DEFAULT:
                if prec in self._defaults_by_precedence:
                    raise MultiplePrecedenceError(
                        f"Error: multiple defaults supplied for precedence {prec}: {self._defaults_by_precedence[prec]}, {output_tag_spec}"
                    )
                self._defaults_by_precedence[prec] = output_tag_spec
            else:
                if output_tag_spec == TagMap.COPY_TAG_NAME:
                    assert input_tag_spec.startswith(
                        "+"
                    ), f"expected tag to start with + but did not: {input_tag_spec}"
                    output_tag_spec = input_tag_spec[1:] + "+"
                self._tag_mapping[input_tag_spec] = output_tag_spec

            if output_tag_spec is not None:
                if output_tag_spec in self._precedences:
                    if prec != self._precedences[output_tag_spec]:
                        raise ConflictingPrecedenceError(
                            f"Error: conflicting precedences specified for {output_tag_spec!r}: {self._precedences[output_tag_spec]} and {prec}"
                        )
                else:
                    self._precedences[output_tag_spec] = prec

    def map_tags(self, input_tags):
        output_tags = []

        # copy input, because we may mutate it
        input_tags = input_tags[:]

        # first handle multi-mappings, which consume their matching input
        # tags so that they are not re-considered in the next steps
        for input_tag_spec, output_tag_spec, prec in self._multi_mappings:
            if is_subsequence(input_tags, input_tag_spec):
                if output_tag_spec is not None:
                    output_tags.append(output_tag_spec)
                input_tags = [x for x in input_tags if x not in input_tag_spec]

        # normal mapping
        for input_tag in input_tags:
            try:
                output_tag = self._tag_mapping[input_tag]
            except KeyError:
                raise UnknownTagError(input_tag)
            if output_tag is not None and output_tag not in output_tags:
                output_tags.append(output_tag)

        # if no mapping for a precedence, use default
        used_precedences = set(self._precedences[tag] for tag in output_tags)
        for prec, default in self._defaults_by_precedence.items():
            if prec not in used_precedences:
                output_tags.append(default)

        # Sort all the combined output tags generated by all previous steps
        # into precedence order
        output_tags.sort(key=self._precedences.__getitem__)

        return _flatten_tuples(output_tags)


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

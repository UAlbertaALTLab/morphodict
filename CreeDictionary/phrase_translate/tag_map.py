# https://stackoverflow.com/a/52709319/14558
def is_subsequence(outer_list, target_subsequence):
    it = iter(outer_list)
    return all(x in it for x in target_subsequence)


class TagMap:
    DEFAULT = object()
    COPY = object()

    def __init__(self, *tag_definitions):
        """
        See the docs in crk_tag_map.py.
        """
        self._tag_mapping = {}
        self._multi_mappings = []
        self._precedences = {}
        self._defaults_by_precedence = {}

        for k, v, prec in tag_definitions:
            if isinstance(k, tuple):
                if v == TagMap.COPY:
                    raise Exception(f"Error: cannot use copy with multi-tags: {k}")
                self._multi_mappings.append((k, v, prec))
            elif k == TagMap.DEFAULT:
                if prec in self._defaults_by_precedence:
                    raise Exception(
                        f"Error: multiple defaults supplied for precedence {prec}: {self._defaults_by_precedence[prec]}, {v}"
                    )
                self._defaults_by_precedence[prec] = v
            else:
                if v == TagMap.COPY:
                    v = k[1:] + "+"
                self._tag_mapping[k] = v

            if v is not None:
                if v in self._precedences:
                    if prec != self._precedences[v]:
                        raise Exception(
                            f"Error: conflicting precedences specified for {v!r}: {self._precedences[v]} and {prec}"
                        )
                else:
                    self._precedences[v] = prec

    def map_tags(self, input_tags):
        tags_for_phrase = []

        # copy input, because we may mutate it
        input_tags = input_tags[:]

        # handle multi-mappings
        for k, v, prec in self._multi_mappings:
            if is_subsequence(input_tags, k):
                if v is not None:
                    tags_for_phrase.append(v)
                input_tags = [x for x in input_tags if x not in k]

        # normal mapping
        for wordform_tag in input_tags:
            phrase_tag = self._tag_mapping[wordform_tag]
            if phrase_tag is not None and phrase_tag not in tags_for_phrase:
                tags_for_phrase.append(phrase_tag)

        # if no mapping for a precedence, use default
        used_precedences = set(self._precedences[tag] for tag in tags_for_phrase)
        for prec, default in self._defaults_by_precedence.items():
            if prec not in used_precedences:
                tags_for_phrase.append(default)

        tags_for_phrase.sort(key=lambda tag: self._precedences[tag])

        return tags_for_phrase

# https://stackoverflow.com/a/52709319/14558
def is_subsequence(outer_list, target_subsequence):
    it = iter(outer_list)
    return all(x in it for x in target_subsequence)


class TagMap:
    def __init__(self, *tag_definitions):
        """
        See the docs in crk_tag_map.py.
        """
        self._tag_mapping = {}
        self._multi_mappings = []
        self._precedences = {}

        for k, v, prec in tag_definitions:
            if isinstance(k, tuple):
                self._multi_mappings.append((k, v, prec))
            else:
                if v == "copy":
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

        for k, v, prec in self._multi_mappings:
            if is_subsequence(input_tags, k):
                tags_for_phrase.append(v)
                input_tags = [x for x in input_tags if x not in k]

        for wordform_tag in input_tags:
            phrase_tag = self._tag_mapping[wordform_tag]
            if phrase_tag is not None and phrase_tag not in tags_for_phrase:
                tags_for_phrase.append(phrase_tag)

        tags_for_phrase.sort(key=lambda tag: self._precedences[tag])

        return tags_for_phrase

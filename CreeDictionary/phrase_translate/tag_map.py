class TagMap:
    def __init__(self, *tag_definitions):
        """
        See the docs in crk_tag_map.py.
        """
        self._tag_mapping = {}
        self._precedences = {}

        for k, v, prec in tag_definitions:
            if v == "copy":
                v = k[1:] + "+"
            self._tag_mapping[k] = v

            if v is not None:
                self._precedences[v] = prec

    def map_tags(self, input_tags):
        tags_for_phrase = []

        for wordform_tag in input_tags:
            phrase_tag = self._tag_mapping[wordform_tag]
            if phrase_tag is not None and phrase_tag not in tags_for_phrase:
                tags_for_phrase.append(phrase_tag)

        tags_for_phrase.sort(key=lambda tag: self._precedences[tag])

        return tags_for_phrase

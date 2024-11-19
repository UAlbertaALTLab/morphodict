"""
Source language-specific data for English Inflected Phrase search
"""

from morphodict.analysis.tag_map import TagMap
from django.conf import settings
import json
import re


def read_phrase_translate_json(filename, default=[]):
    # This helper function parses the contents of our phrase_translate elements *after* removing comments.
    # Note that, in general, this might interact with the JSON file contents, but we are not using # for
    # anything in our json files yet, so we can use them.
    try:
        with open(
            settings.BASE_DIR / "resources" / "phrase_translate" / filename, "r"
        ) as f:
            contents = f.read()
            ans = json.loads(re.sub("(^|\s)+#.*\n", "", contents))
    except FileNotFoundError:
        return default
    return ans


# tags needed for FST generator
source_noun_tags = read_phrase_translate_json("noun_tags.json")


# TagMaps can’t automatically pass through unknown tags because they wouldn’t
# know how to order the unknown tags amongst the defined precedence classes. For
# example, when populating a default tense tag of +Ind, it has to put that after
# +V+TA and before +1Sg, so it needs precedence values for all of those tags.
#
# So we list everything.
noun_passthrough_tags = read_phrase_translate_json("noun_passthrough_tags.json", {})

verb_passthrough_tags = read_phrase_translate_json("verb_passthrough_tags.json", {})


def passthrough_tags_to_tuples(passthrough_tags):
    return (
        (tag, tag, int(precedence))
        for precedence, tag_list in passthrough_tags.items()
        for tag in tag_list
    )


def lists_to_tuple(l):
    def element_process(x):
        if isinstance(x, list):
            return tuple(x)
        if x == "TagMap.DEFAULT":
            return TagMap.DEFAULT
        if x == "TagMap.COPY_TAG_NAME":
            return TagMap.COPY_TAG_NAME
        return x

    return tuple(element_process(x) for x in l)


def tagmap_json_to_tuples(json):
    return [lists_to_tuple(t) for t in json]


verb_tag_map = TagMap(
    *tagmap_json_to_tuples(read_phrase_translate_json("verb_tag_map.json")),
    *passthrough_tags_to_tuples(verb_passthrough_tags)
)

noun_tag_map = TagMap(
    *tagmap_json_to_tuples(read_phrase_translate_json("noun_tag_map.json")),
    *passthrough_tags_to_tuples(noun_passthrough_tags)
)

from morphodict.phrase_translate.tag_maps import *

noun_wordform_to_phrase = TagMap(
    *tagmap_json_to_tuples(read_phrase_translate_json("noun_wordform_to_phrase.json")),
)

# Normally having a preverb tag excludes a wordform from auto-translation; this
# list specifies exceptions to that rule for grammatical preverbs.
#
# (This could be automatically extracted from the TagMap object.)
permitted_preverb_tags = {"PV/e+", "PV/ki+", "PV/ka+", "PV/ta+", "PV/wi+"}

# Cree tense/aspects:
verb_wordform_to_phrase = TagMap(
    *tagmap_json_to_tuples(read_phrase_translate_json("verb_wordform_to_phrase.json")),
)

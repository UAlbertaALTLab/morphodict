from CreeDictionary.phrase_translate.tag_map import TagMap

## Motivation
#
# TagMap handles the mapping from analysis FST tags to phrase-generation
# FST tags. As the wordform analysis and phrase-generation FSTs do fairly
# different things, using different but related sets of tags, we need to specify
# how to translate from one to the other.
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
# A TagMap is iniialized with a sequence of (wordform_tag, phrase_tag,
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

COPY_TAG_NAME = TagMap.COPY_TAG_NAME

noun_wordform_to_phrase = TagMap(
    ("+N", None, 0),
    ("+A", None, 0),
    ("+I", None, 0),
    ("+D", None, 0),
    # Number
    ("+Sg", COPY_TAG_NAME, 1),
    ("+Pl", COPY_TAG_NAME, 1),
    ("+Obv", COPY_TAG_NAME, 1),
    ("+Loc", COPY_TAG_NAME, 1),
    ("+Distr", COPY_TAG_NAME, 1),
    # Diminutive
    ("+Dim", COPY_TAG_NAME, 2),
    ("+Der/Dim", "Dim+", 2),
    # Possessives
    ("+Px1Sg", COPY_TAG_NAME, 3),
    ("+Px2Sg", COPY_TAG_NAME, 3),
    ("+Px3Sg", COPY_TAG_NAME, 3),
    ("+Px1Pl", COPY_TAG_NAME, 3),
    ("+Px2Pl", COPY_TAG_NAME, 3),
    ("+Px12Pl", COPY_TAG_NAME, 3),
    ("+Px3Pl", COPY_TAG_NAME, 3),
    ("+Px4Sg/Pl", COPY_TAG_NAME, 3),
    ("+PxX", COPY_TAG_NAME, 3),
)

# Cree tense/aspects:
verb_wordform_to_phrase = TagMap(
    ("+V", None, 0),
    ("+TA", None, 0),
    ("+AI", None, 0),
    ("+II", None, 0),
    ("+TI", None, 0),
    # Tense/Aspect
    ("PV/ki+", "Prt+", 1),  # Preterite aka simple past
    (("PV/ki+", "+Ind"), "Prt+", 1),  # Preterite aka simple past
    (("+Fut", "+Cond"), "Cond+", 1),  # Future conditional
    (("+Imp", "+Imm"), "Imm+", 1),  # Immediate imperative
    (("+Imp", "+Del"), "Del+", 1),  # Delayed imperative
    (("PV/wi+", "+Ind"), "Fut+", 1),  # Future
    ("PV/wi+", "Fut+", 1),  # Also accept PV/wi without indicative as future
    (("PV/e+", "+Cnj"), None, 1),  # conjunctive marker
    # Note that these crk features as disjoint, but both are needed for the eng feature
    (("PV/ka+", "+Ind"), "Def+", 1),
    (("PV/ka+", "+Cnj"), "Inf+", 1),
    (("PV/ta+", "+Cnj"), "Inf+", 1),  # future definite
    ("+Ind", "Prs+", 1),
    (TagMap.DEFAULT, "Prs+", 1),  # default to present tense
    # Person - Subject
    ("+1Sg", COPY_TAG_NAME, 2),
    ("+2Sg", COPY_TAG_NAME, 2),
    ("+3Sg", COPY_TAG_NAME, 2),
    ("+1Pl", COPY_TAG_NAME, 2),
    ("+12Pl", "21Pl+", 2),
    ("+2Pl", COPY_TAG_NAME, 2),
    ("+3Pl", COPY_TAG_NAME, 2),
    ("+4Sg/Pl", COPY_TAG_NAME, 2),
    ("+5Sg/Pl", COPY_TAG_NAME, 2),
    ("+X", COPY_TAG_NAME, 2),
    # Person - Object
    ("+1SgO", COPY_TAG_NAME, 3),
    ("+2SgO", COPY_TAG_NAME, 3),
    ("+3SgO", COPY_TAG_NAME, 3),
    ("+1PlO", COPY_TAG_NAME, 3),
    ("+12PlO", "21PlO+", 3),
    ("+2PlO", COPY_TAG_NAME, 3),
    ("+3PlO", COPY_TAG_NAME, 3),
    ("+4Pl", COPY_TAG_NAME, 3),
    ("+4Sg", COPY_TAG_NAME, 3),
    ("+4Sg/PlO", COPY_TAG_NAME, 3),
    ("+5Sg/PlO", COPY_TAG_NAME, 3),
    ("+XO", COPY_TAG_NAME, 3),
)

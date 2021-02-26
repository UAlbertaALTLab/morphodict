from phrase_translate.tag_map import TagMap

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
#   - COPY if the characters of the wordform_tag match the phrase_tag, for
#     example: ("+Sg", COPY, x) means ("+Sg", "Sg+", x)
#
# The precedence number is used to sort tags before sending to the phrase FST,
# so if you want Pl/Sg before Px, you could give Pl and Sg number 1 and the
# possessives number 2. This precedence number is associated with the output
# tag; it is an error to give a different precedence value to multiple
# definitions that output the same tag.

COPY = TagMap.COPY

noun_wordform_to_phrase = TagMap(
    ("+N", None, 0),
    ("+A", None, 0),
    ("+I", None, 0),
    ("+D", None, 0),
    # Number
    ("+Sg", COPY, 1),
    ("+Pl", COPY, 1),
    ("+Obv", COPY, 1),
    ("+Loc", COPY, 1),
    ("+Distr", COPY, 1),
    # Diminutive
    ("+Dim", COPY, 2),
    ("+Der/Dim", "Dim+", 2),
    # Possessives
    ("+Px1Sg", COPY, 3),
    ("+Px2Sg", COPY, 3),
    ("+Px3Sg", COPY, 3),
    ("+Px1Pl", COPY, 3),
    ("+Px2Pl", COPY, 3),
    ("+Px12Pl", COPY, 3),
    ("+Px3Pl", COPY, 3),
    ("+Px4Sg/Pl", COPY, 3),
    ("+PxX", COPY, 3),
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
    (("PV/wi+", "+Ind"), "Int+", 1),  # Intentional
    ("PV/wi+", "Int+", 1),  # Also accept PV/wi without indicative as intentional
    (("PV/e+", "+Cnj"), None, 1),  # conjunctive marker
    # Note that these crk features as disjoint, but both are needed for the eng feature
    (("PV/ka+", "+Ind"), "Fut+", 1),
    (("PV/ka+", "+Cnj"), "Inf+", 1),
    (("PV/ta+", "+Cnj"), "Inf+", 1),  # future definite
    (TagMap.DEFAULT, "Prs+", 1),  # default to present tense
    # Person - Subject
    ("+1Sg", COPY, 2),
    ("+2Sg", COPY, 2),
    ("+3Sg", COPY, 2),
    ("+1Pl", COPY, 2),
    ("+12Pl", "21Pl+", 2),
    ("+2Pl", COPY, 2),
    ("+3Pl", COPY, 2),
    ("+4Sg/Pl", COPY, 2),
    ("+5Sg/Pl", COPY, 2),
    ("+X", COPY, 2),
    # Person - Object
    ("+1SgO", COPY, 3),
    ("+2SgO", COPY, 3),
    ("+3SgO", COPY, 3),
    ("+1PlO", COPY, 3),
    ("+2PlO", COPY, 3),
    ("+3PlO", COPY, 3),
    ("+4Sg/PlO", COPY, 3),
    ("+5Sg/PlO", COPY, 3),
    ("+XO", COPY, 3),
)

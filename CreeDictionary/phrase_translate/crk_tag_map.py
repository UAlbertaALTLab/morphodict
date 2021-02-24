from phrase_translate.tag_map import TagMap

# A TagMap is iniialized with a sequence of (wordform_tag, phrase_tag,
# precedence) tuples
#
# wordform_tag can be:
#   - A literal tag, e.g., "N+", which will be matched exactly
#   - A tuple of tags, e.g., ("PV/e+, "+Ind") which will be matched as a
#     subsequence
#
# phrase_tag can be:
#   - None if the wordform_tag is not used in the phrase transcription
#   - "copy" if the characters of the wordform_tag match the phrase_tag, for
#     example: ("+Sg", "copy", x) means ("+Sg", "Sg+", x)
#
# The precedence number is used to sort tags before sending to the phrase FST,
# so if you want Pl/Sg before Px, you could give Pl and Sg number 1 and the
# possessives number 2. This precedence number is associated with the output
# tag; it is an error to give a different precedence value to multiple
# definitions that output the same tag.

noun_wordform_to_phrase = TagMap(
    ("+N", None, 0),
    ("+A", None, 0),
    ("+I", None, 0),
    ("+D", None, 0),
    # Number
    ("+Sg", "copy", 1),
    ("+Pl", "copy", 1),
    ("+Obv", "copy", 1),
    ("+Loc", "copy", 1),
    ("+Distr", "copy", 1),
    # Diminutive
    ("+Dim", "copy", 2),
    ("+Der/Dim", "Dim+", 2),
    # Possessives
    ("+Px1Sg", "copy", 3),
    ("+Px2Sg", "copy", 3),
    ("+Px3Sg", "copy", 3),
    ("+Px1Pl", "copy", 3),
    ("+Px2Pl", "copy", 3),
    ("+Px12Pl", "copy", 3),
    ("+Px3Pl", "copy", 3),
    ("+Px4Sg/Pl", "copy", 3),
    ("+PxX", "copy", 3),
)

verb_wordform_to_phrase = TagMap(
    ("+V", None, 0),
    ("+TA", None, 0),
    ("+AI", None, 0),
    ("+II", None, 0),
    ("+TI", None, 0),
    ("+Ind", None, 0),
    # Tense/Aspect
    ("+Cond", "copy", 1),
    ("+Imm", "copy", 1),
    ("+Del+", "copy", 1),
    ("PV/ki+", "Prt+", 1),
    ("PV/wi+", "Int+", 1),
    # Note that these crk features as disjoint, but both are needed for the eng feature
    (("PV/ka+", "+Ind"), "Fut+", 1),
    (("PV/e+", "+Cnj"), "Prs+", 1),  # ← I am not sure about this one, please check
    # ("PV/ka+...+Cnj", "Inf+", 1),
    # ("PV/ta+...+Cnj", "Inf+", 1),
    # We would need a default assignment, if none of the above options are matched
    # ("", "Prs+",1),
    # Person - Subject
    ("+1Sg", "copy", 2),
    ("+2Sg", "copy", 2),
    ("+3Sg", "copy", 2),
    ("+1Pl", "copy", 2),
    ("+2Pl", "copy", 2),
    ("+3Pl", "copy", 2),
    ("+4Sg/Pl", "copy", 2),
    ("+5Sg/Pl", "copy", 2),
    ("+X", "copy", 2),
    # Person - Object
    ("+1SgO", "copy", 3),
    ("+2SgO", "copy", 3),
    ("+3SgO", "copy", 3),
    ("+1PlO", "copy", 3),
    ("+2PlO", "copy", 3),
    ("+3PlO", "copy", 3),
    ("+4Sg/PlO", "copy", 3),
    ("+5Sg/PlO", "copy", 3),
    ("+XO", "copy", 3),
)

from phrase_translate.tag_map import TagMap

# A TagMap is iniialized with a sequence of (wordform_tag, phrase_tag,
# precedence) tuples
#
# phrase_tag can be:
#   - None if the wordform_tag is not used in the phrase transcription
#   - "copy" if the characters of the wordform_tag match the phrase_tag, for
#     example: ("+Sg", "copy", x) means ("+Sg", "Sg+", x)
#
# The precedence number is used to sort tags before sending to the phrase FST,
# so if you want Pl/Sg before Px, you could give Pl and Sg number 1 and the
# possessives number 2.

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
    # ! 1: Tense/Aspect: Prs+ (+Ind and +Cnj), Prt+ (PV/ki), Fut+ (PV/ka+), Int+ (PV/w
    # i), Cond+ (+Fut+Cond), Inf+ (PV/ka+...+Cnj, PV/ta+...+Cnj), Imm+ (Imp+Imm), Del+
    #  (Imp+Del+)
    # ! 2: Actor: 1Sg+, 2Sg+, 3Sg+, 1Pl+, 12Pl+, 2Pl+, 3Pl+, X+, 4Sg+, 4Pl+, 4Sg/Pl+,
    # 5Sg/Pl+
    # ! 3: Goal (optional): 1SgO+, 2SgO+, 3SgO+, 1PlO+, 12PlO+, 2PlO+, 3PlO+, XO+, 4Sg
    # /PlO+, 5Sg/PlO+
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
    ("+Imp", "Imm+", 1),
    # Actor
    ("+1Pl", "copy", 2),
    ("+2Sg", "copy", 2),
    ("+3Sg", "copy", 2),
    ("+4Sg/Pl", "copy", 2),
    ("+2PlO", "copy", 2),
    ("+3Pl", "copy", 2),
    # Goal
    ("+4Sg/PlO", "copy", 3),
)

# verb_wordform_to_phrase_tag_info = (
# Tense/Aspect
#     ("PV/ki+", "Prt+", 1),
#     ("PV/wi+", "Int+"", 1)
#     ("+Cond", "Cond+"", 1)
#     ("+Imm", "Imm+"", 1)
#     ("+Del+", "Del+"", 1)
#     Note that these crk features as disjoint, but both are needed for the eng feature
#     ("PV/ka+...+Ind", "Fut+", 1)
#     ("PV/ka+...+Cnj", "Inf+", 1)
#     ("PV/ta+...+Cnj", "Inf+", 1)
# We would need a default assignment, if none of the above options are matched
#     ("", "Prs+",1),
# Person - Subject
#     ("+1Sg", "", 2)
#     ("+2Sg", "", 2)
#     ("+3Sg", "", 2)
#     ("+1Pl", "", 2)
#     ("+2Pl", "", 2)
#     ("+3Pl", "", 2)
#     ("+4Sg/Pl", "", 2)
#     ("+5Sg/Pl", "", 2)
#     ("+X", "", 2)
# Person - Object
#     ("+1SgO", "", 3)
#     ("+2SgO", "", 3)
#     ("+3SgO", "", 3)
#     ("+1PlO", "", 3)
#     ("+2PlO", "", 3)
#     ("+3PlO", "", 3)
#     ("+4Sg/PlO", "", 3)
#     ("+5Sg/PlO", "", 3)
#     ("+XO", "", 3),
# )

from morphodict.analysis.tag_map import TagMap

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
    ("+Px12Pl", COPY_TAG_NAME, 3),  # Maybe needs to be recoded with 12 -> 21
    ("+Px3Pl", COPY_TAG_NAME, 3),
    ("+Px4Sg/Pl", COPY_TAG_NAME, 3),
    ("+PxX", "PxXPl+", 3),
)

# Normally having a preverb tag excludes a wordform from auto-translation; this
# list specifies exceptions to that rule for grammatical preverbs.
#
# (This could be automatically extracted from the TagMap object.)
permitted_preverb_tags = {"PV/e+", "PV/ki+", "PV/ka+", "PV/ta+", "PV/wi+"}

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
    ("+X", "+XPl", 2),
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
    ("+XO", "+XPlO", 3),
)

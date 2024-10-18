"""
Cree-specific data for English Inflected Phrase search
"""

from morphodict.analysis.tag_map import TagMap

# tags needed for FST generator
crk_noun_tags = ["+N", "+A", "+I", "+D"]


# TagMaps can’t automatically pass through unknown tags because they wouldn’t
# know how to order the unknown tags amongst the defined precedence classes. For
# example, when populating a default tense tag of +Ind, it has to put that after
# +V+TA and before +1Sg, so it needs precedence values for all of those tags.
#
# So we list everything.
noun_passthrough_tags = {
    0: [
        # word class
        "+N",
        "+A",
        "+I",
        "+D",
    ],
    2: [
        # N: Possessives
        "+Px1Sg",
        "+Px2Sg",
        "+Px3Sg",
        "+Px1Pl",
        "+Px2Pl",
        # "+Px12Pl", # Needs to be recoded: 21 -> 12
        "+Px3Pl",
        "+Px4Sg/Pl",
        "+PxX",
        "+PxXPl",
    ],
    3: [
        # N: number
        "+Sg",
        "+Pl",
        "+Obv",
        "+Loc",
        "+Distr",
    ],
}

verb_passthrough_tags = {
    0: [
        # word class
        "+V",
        "+TA",
        "+AI",
        "+II",
        "+TI",
    ],
    2: [
        # V: Person - subject
        "+1Sg",
        "+2Sg",
        "+3Sg",
        "+1Pl",
        # "+12Pl", # Needs to be recoded: 21 -> 12
        "+2Pl",
        "+3Pl",
        "+4Sg/Pl",
        "+5Sg/Pl",
        "+X",
        "+XPl",
    ],
    3: [
        # V: Person - object
        "+1SgO",
        "+2SgO",
        "+3SgO",
        "+1PlO",
        # "+21PlO", # Needs to be recoded: 21 -> 12
        "+2PlO",
        "+3PlO",
        "+4Pl",
        "+4Sg",
        "+4Sg/PlO",
        "+5Sg/PlO",
        "+XO",
        "+XPlO",
    ],
}


def passthrough_tags_to_tuples(passthrough_tags):
    return (
        (tag, tag, precedence)
        for precedence, tag_list in passthrough_tags.items()
        for tag in tag_list
    )


verb_tag_map = TagMap(
    # Tense
    ("+Prt", ("PV/ki+", "+Ind"), 1),  # Preterite aka simple past
    ("+Cond", ("+Fut", "+Cond"), 1),  # Future conditional
    ("+Imm", ("+Imp", "+Imm"), 1),  # Immediate imperative
    ("+Del", ("+Imp", "+Del"), 1),  # Delayed imperative
    ("+Fut", ("PV/wi+", "+Ind"), 1),  # Future
    # TODO: also handle ("+Fut", "PV/wi+", 1)  # Also accept PV/wi without independent as future?
    # Note that these crk features as disjoint, but both are needed for the eng feature
    ("+Def", ("PV/ka+", "+Ind"), 1),
    ("+Inf", ("PV/ka+", "+Cnj"), 1),
    (TagMap.DEFAULT, "+Ind", 1),
    # Person - see https://github.com/UAlbertaALTLab/morphodict/issues/891
    ("+0Sg", "+3Sg", 2),
    (
        "+21Pl",
        "+12Pl",
        2,
    ),  # see https://github.com/UAlbertaALTLab/morphodict/issues/1005
    ("+XPl", "+X", 2),
    # Person - object
    ("+0SgO", (), 3),
    (
        "+21PlO",
        "+12PlO",
        3,
    ),
    ("+XPlO", "+XO", 3),
    (
        "+PV/pimi",
        ("PV/pimi+"),
        3,
    ),  # see https://github.com/UAlbertaALTLab/morphodict/issues/1005
    # TODO: also handle "+Inf": ("PV/ta+", "+Cnj")  # future definite?
    *passthrough_tags_to_tuples(verb_passthrough_tags)
)

noun_tag_map = TagMap(
    ("+Dim", "+Der/Dim", 2),
    ("+Px21Pl", "+Px12Pl", 2),
    ("+PxXPl", "+PxX", 2),
    *passthrough_tags_to_tuples(noun_passthrough_tags)
)

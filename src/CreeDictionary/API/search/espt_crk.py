"""
Cree-specific data for English Inflected Phrase search
"""
from morphodict.analysis.tag_map import TagMap


def get_noun_tags(inflectional_category: str):
    """Turn a wordform’s inflectional class into tags needed for FST generator.

    >>> get_noun_tags("NA")
    '+N+A'
    >>> get_noun_tags("NA-3")
    '+N+A'
    >>> get_noun_tags("ND")
    '+N+D'
    """
    noun_tags = ""
    for c in inflectional_category:
        if c == "-":
            return noun_tags
        noun_tags += "+" + c

    return noun_tags


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
        "+Px12Pl",
        "+Px3Pl",
        "+Px4Sg/Pl",
        "+PxX",
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
        "+12Pl",
        "+2Pl",
        "+3Pl",
        "+4Sg/Pl",
        "+5Sg/Pl",
        "+X",
    ],
    3: [
        # V: Person - object
        "+1SgO",
        "+2SgO",
        "+3SgO",
        "+1PlO",
        "21PlO+",
        "+2PlO",
        "+3PlO",
        "+4Pl",
        "+4Sg",
        "+4Sg/PlO",
        "+5Sg/PlO",
        "+XO",
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
    # TODO: also handle "+Inf": ("PV/ta+", "+Cnj")  # future definite?
    *passthrough_tags_to_tuples(verb_passthrough_tags)
)

noun_tag_map = TagMap(
    ("+Dim", "+Der/Dim", 2), *passthrough_tags_to_tuples(noun_passthrough_tags)
)


crkeng_tag_dict = {
    "+Prt": ("PV/ki+", "+Ind"),  # Preterite aka simple past
    "+Cond": ("+Fut", "+Cond"),  # Future conditional
    "+Imm": ("+Imp", "+Imm"),  # Immediate imperative
    "+Del": ("+Imp", "+Del"),  # Delayed imperative
    "+Fut": ("PV/wi+", "+Ind"),  # Future
    # TODO: also handle "+Fut": "PV/wi+",  # Also accept PV/wi without independent as future?
    # Note that these crk features as disjoint, but both are needed for the eng feature
    "+Def": ("PV/ka+", "+Ind"),
    "+Inf": ("PV/ka+", "+Cnj"),
    # TODO: also handle "+Inf": ("PV/ta+", "+Cnj")  # future definite?
    "+Dim": ("+Der/Dim",),
}

# Cree-specific data for English Inflected Phrase search


def get_noun_tags(inflectional_category):
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


crkeng_tag_dict = {
    "+Prt": ("PV/ki+", "+Ind"),  # Preterite aka simple past
    "+Cond": ("+Fut", "+Cond"),  # Future conditional
    "+Imm": ("+Imp", "+Imm"),  # Immediate imperative
    "+Del": ("+Imp", "+Del"),  # Delayed imperative
    "+Fut": ("PV/wi+", "+Ind"),  # Future
    # "+Fut": "PV/wi+",  # Also accept PV/wi without indicative as future
    # Note that these crk features as disjoint, but both are needed for the eng feature
    "+Def": ("PV/ka+", "+Ind"),
    "+Inf": ("PV/ka+", "+Cnj"),
    # "+Inf": ("PV/ta+", "+Cnj")  # future definite
    "+Dim": ("+Der/Dim",),
}

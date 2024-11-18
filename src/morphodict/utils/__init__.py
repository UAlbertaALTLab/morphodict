from .cree_lev_dist import get_modified_distance  # Unused but exported
from .shared_res_dir import shared_res_dir  # Unused but exported


def macron_to_circumflex(item):
    """
    >>> macron_to_circumflex("wāpamēw")
    'wâpamêw'
    """
    item = item.translate(str.maketrans("ēīōā", "êîôâ"))
    return item

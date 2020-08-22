from typing import List

from utils.fst_analysis_parser import LABELS
from utils.types import FSTTag, Label


def replace_user_friendly_tags(fst_tags: List[FSTTag]) -> List[Label]:
    """ replace fst-tags to cute ones"""
    return LABELS.english.get_full_relabelling(fst_tags)
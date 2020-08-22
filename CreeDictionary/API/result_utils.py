from typing import List

from utils.fst_analysis_parser import LABELS, partition_analysis
from utils.types import FSTTag, Label, ConcatAnalysis


def replace_user_friendly_tags(fst_tags: List[FSTTag]) -> List[Label]:
    """ replace fst-tags to cute ones"""
    return LABELS.english.get_full_relabelling(fst_tags)


def safe_partition_analysis(analysis: ConcatAnalysis):
    try:
        (linguistic_breakdown_head, _, linguistic_breakdown_tail,) = partition_analysis(
            analysis
        )
    except ValueError:
        linguistic_breakdown_head = []
        linguistic_breakdown_tail = []
    return linguistic_breakdown_head, linguistic_breakdown_tail

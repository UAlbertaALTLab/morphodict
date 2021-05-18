#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import CreeDictionary.CreeDictionary.hfstol as temp_hfstol

# TODO: use better imports https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/issues/525
from CreeDictionary.utils.data_classes import Analysis


def test_fst_analysis():
    analyses = set(temp_hfstol.analyze("ta-pe-kiwemakaniyiw"))
    assert (
        Analysis(
            raw_prefixes="PV/ta+PV/pe", lemma="kîwêmakan", raw_suffixes="V+II+Ind+4Sg"
        )
        in analyses
    )


def test_fst_generation():
    wordforms = set(temp_hfstol.generate("PV/ta+PV/pe+kîwêmakan+V+II+Ind+4Sg"))
    assert "ta-pê-kîwêmakaniyiw" in wordforms

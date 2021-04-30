from functools import cache
from pathlib import Path
from typing import Optional

from hfst_optimized_lookup import TransducerFile
from shared import expensive
from utils import shared_res_dir

from CreeDictionary.paradigm.panes import Paradigm, ParadigmTemplate


class ParadigmManager:
    """
    Mediates access to paradigms layouts/templates.
    """

    def __init__(self, layout_directory: Path, generation_fst: TransducerFile):
        # TODO: technically str == ConcatAnalysis
        self._analysis_to_layout: dict[str, ParadigmTemplate] = {}
        self._load_static_from(layout_directory / "static")
        self._generator = generation_fst

    def paradigm_for(self, analysis: str) -> Optional[Paradigm]:
        """
        Given an analysis, returns its paradigm.
        """
        if layout := self._analysis_to_layout.get(analysis):
            return self._inflect(layout)
        return None

    def _load_static_from(self, path: Path):
        """
        Loads all .tsv files in the path as "static" paradigms.
        """

        for layout_file in path.glob("*.tsv"):
            layout = ParadigmTemplate.loads(layout_file.read_text(encoding="UTF-8"))

            for inflection in layout.inflection_cells:
                self._analysis_to_layout[inflection.analysis] = layout

    def _inflect(self, layout: ParadigmTemplate) -> Paradigm:
        analyses = layout.generate_fst_analysis_string(lemma="").splitlines(
            keepends=False
        )
        forms = self._generator.bulk_lookup(analyses)
        return layout.fill(forms)


@cache
def default_paradigm_manager() -> ParadigmManager:
    """
    Returns the ParadigmManager instance that loads layouts from the res (resource) directory
    """
    return ParadigmManager(shared_res_dir / "layouts", expensive.strict_generator)

from pathlib import Path
from typing import Optional

from shared import expensive
from utils import shared_res_dir

from CreeDictionary.paradigm.panes import Paradigm, ParadigmTemplate


class ParadigmManager:
    """
    Mediates access to paradigms layouts/templates.
    """

    def __init__(self):
        # TODO: technically str == ConcatAnalysis
        self._analysis_to_layout: dict[str, ParadigmTemplate] = {}
        self._load_static_from(shared_res_dir / "layouts" / "static")

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

        layouts = []

        for layout_file in path.glob("*.tsv"):
            layout = ParadigmTemplate.loads(layout_file.read_text(encoding="UTF-8"))
            layouts.append(layout)

            for inflection in layout.inflection_cells:
                self._analysis_to_layout[inflection.analysis] = layout

    def _inflect(self, layout: ParadigmTemplate) -> Paradigm:
        analyses = layout.generate_fst_analysis_string(lemma="").splitlines(
            keepends=False
        )
        forms = expensive.strict_generator.bulk_lookup(analyses)
        return layout.fill(forms)

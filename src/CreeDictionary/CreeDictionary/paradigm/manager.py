from functools import cache
from pathlib import Path
from typing import Optional

from hfst_optimized_lookup import TransducerFile
from CreeDictionary.shared import expensive
from CreeDictionary.utils import shared_res_dir

from CreeDictionary.CreeDictionary.paradigm.panes import Paradigm, ParadigmLayout


class ParadigmManager:
    """
    Mediates access to paradigms layouts.

    Loads layouts from the filesystem and can fill the layout with results from a
    (normative/strict) generator FST.
    """

    def __init__(self, layout_directory: Path, generation_fst: TransducerFile):
        self._generator = generation_fst
        self._name_to_layout: dict[str, Paradigm] = {}
        self._wc_to_layout: dict[str, ParadigmLayout] = {}

        self._load_static_from(layout_directory / "static")
        self._load_dynamic_from(layout_directory / "dynamic")

    def static_paradigm_for(self, name: str) -> Optional[Paradigm]:
        """
        Returns a static paradigm with the given name.
        Returns None if there is no paradigm with such a name.
        """
        return self._name_to_layout.get(name)

    def dynamic_paradigm_for(self, *, lemma: str, word_class: str) -> Optional[Paradigm]:
        """
        Returns a dynamic paradigm for the given lemma and word class.
        Returns None if no such paradigm can be generated.
        """
        if layout := self._wc_to_layout.get(word_class):
            return self._inflect(layout, lemma)

        # No matching word class means no paradigm:
        return None

    def _load_static_from(self, path: Path):
        """
        Loads all .tsv files in the path as "static" paradigms.
        """

        for layout_file in path.glob("*.tsv"):
            layout = ParadigmLayout.loads(layout_file.read_text(encoding="UTF-8"))
            self._name_to_layout[layout_file.stem] = layout.as_static_paradigm()

    def _load_dynamic_from(self, path: Path):
        """
        Loads all .tsv files as dynamic layouts.
        """
        for layout_file in path.glob("*.tsv"):
            layout = ParadigmLayout.loads(layout_file.read_text(encoding="UTF-8"))
            self._wc_to_layout[layout_file.stem] = layout

    def _inflect(self, layout: ParadigmLayout, lemma: str) -> Paradigm:
        analyses = layout.generate_fst_analysis_string(lemma=lemma).splitlines(
            keepends=False
        )
        # TODO: need to connect minôs+N+A+Sg to ${lemma}+N+A+Sg somehow
        forms = self._generator.bulk_lookup(analyses)
        return layout.fill(forms)


@cache
def default_paradigm_manager() -> ParadigmManager:
    """
    Returns the ParadigmManager instance that loads layouts and FST from the res
    (resource) directory.
    """
    return ParadigmManager(shared_res_dir / "layouts", expensive.strict_generator)

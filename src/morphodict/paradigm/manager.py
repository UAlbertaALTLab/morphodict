from __future__ import annotations

import logging
import re
from functools import cache
from pathlib import Path
from typing import Collection, Iterable, Optional, Protocol

from django.conf import settings

from morphodict.paradigm.panes import Paradigm, ParadigmLayout

# I would *like* a singleton for this, but, currently, it interacts poorly with mypy :/
ONLY_SIZE = "<only-size>"

logger = logging.getLogger(__name__)


class ParadigmDoesNotExistError(Exception):
    """
    Raised when a paradigm is requested, but does not exist.
    """


class ParadigmManager:
    """
    Mediates access to paradigms layouts.

    Loads layouts from the filesystem and can fill the layout with results from a
    (normative/strict) generator FST.
    """

    # Mappings of paradigm name => sizes available => the layout
    _name_to_layout: dict[str, dict[str, ParadigmLayout]]

    def __init__(self, layout_directory: Path, generation_fst: Transducer):
        self._generator = generation_fst
        self._name_to_layout: dict[str, ParadigmLayout] = {}

        self._load_layouts_from(layout_directory)

    def paradigm_for(
        self,
        paradigm_name: str,
        lemma: Optional[str] = None,
        size: Optional[str] = None,
    ) -> Paradigm:
        """
        Returns a paradigm for the given paradigm name. If a lemma is given, this is
        substituted into the dynamic paradigm.

        :raises ParadigmDoesNotExistError: when the paradigm name cannot be found.
        """
        layout_sizes = self._layout_sizes_or_raise(paradigm_name)
        if size is None:
            size = self.default_size(paradigm_name)

        if size not in layout_sizes:
            raise ParadigmDoesNotExistError(f"size {size!r} for {paradigm_name}")
        layout = layout_sizes[size]

        if lemma is not None:
            return self._inflect(layout, lemma)
        else:
            return layout.as_static_paradigm()

    def sizes_of(self, paradigm_name: str) -> Collection[str]:
        """
        Returns the size options of the given paradigm.

        :raises ParadigmDoesNotExistError: when the paradigm name cannot be found.
        """
        return self._layout_sizes_or_raise(paradigm_name).keys()

    def all_analyses(self, paradigm_name: str, lemma: str) -> set[str]:
        """
        Returns all analysis strings for a given paradigm and lemma in all layout sizes.

        For example, in Plains Cree, you want all analyses for mîcisow (VAI):

            {"mîcisow+V+AI+Ind+Prs+1Sg", "mîcisow+V+AI+Ind+Prs+2Sg", ...}

        :raises ParadigmDoesNotExistError: when the paradigm name cannot be found.
        """

        analyses: set[str] = set()
        for layout in self._layout_sizes_or_raise(paradigm_name).values():
            analyses.update(layout.generate_fst_analyses(lemma).values())

        return analyses

    def default_size(self, paradigm_name: str):
        sizes = list(self.sizes_of(paradigm_name))
        return sizes[0]

    def _layout_sizes_or_raise(self, paradigm_name) -> dict[str, ParadigmLayout]:
        """
        Returns the sizes of the paradigm with the given name.

        :raises ParadigmDoesNotExistError: when the paradigm name cannot be found.
        """
        try:
            return self._name_to_layout[paradigm_name]
        except KeyError:
            raise ParadigmDoesNotExistError(paradigm_name)

    def _load_layouts_from(self, path: Path):
        """
        Loads all .tsv files in the path as paradigm layouts.

        Does nothing if the directory does not exist.
        """
        if not path.exists():
            logger.debug("No layouts found in %s", path)
            return

        for paradigm_name, size, layout in _load_all_layouts_in_directory(path):
            # .setdefault() creates a new, empty dict if the paradigm name does not
            # exist yet:
            self._name_to_layout.setdefault(paradigm_name, {})[size] = layout

    _LITERAL_LEMMA_RE = re.compile(r"\$\{lemma\}")

    @cache
    def all_analysis_template_tags(self, paradigm_name) -> Collection[tuple]:
        """Return the set of all analysis templates in layouts of paradigm_name

        If a paradigm has two sizes, one with template `${lemma}+A` and the
        other with both `${lemma}+A` and `X+${lemma}+B`, then this function will
        return {((), ("+A",)), (("X+",), ("+B",)}.

        Note that these analyses are meant to be inputs to a generator FST for
        building a paradigm table, not the results of analyzing some input
        string.
        """
        ret = {}
        for layout in self._name_to_layout[paradigm_name].values():
            # The trick here is that we can look for a literal `${lemma}`
            # instead of having to parse arbitrary FST analyses.
            for template in layout.generate_fst_analyses("${lemma}"):
                prefix, suffix = self._LITERAL_LEMMA_RE.split(template)

                if settings.MORPHODICT_TAG_STYLE == "Plus":
                    prefix_tags = prefix.split("+")
                    assert (
                        prefix_tags[-1] == ""
                    ), f"Prefix {prefix!r} did not end with +"
                    suffix_tags = suffix.split("+")
                    assert suffix_tags[0] == "", f"Suffix {suffix!r} did not end with +"
                    ret[template] = (
                        tuple(t + "+" for t in prefix_tags[:-1]),
                        tuple("+" + t for t in suffix_tags[1:]),
                    )
                elif settings.MORPHODICT_TAG_STYLE == "Bracket":
                    ret[template] = (split_brackets(prefix), split_brackets(suffix))
                else:
                    raise Exception(f"Unsupported {settings.MORPHODICT_TAG_STYLE=!r}")
        return ret.values()

    def _inflect(self, layout: ParadigmLayout, lemma: str) -> Paradigm:
        """
        Given a layout and a lemma, produce a paradigm with forms generated by the FST.
        """
        template2analysis = layout.generate_fst_analyses(lemma=lemma)
        analysis2forms = self._generator.bulk_lookup(list(template2analysis.values()))
        template2forms = {
            template: analysis2forms[analysis]
            for template, analysis in template2analysis.items()
        }
        return layout.fill(template2forms)


_BRACKET_SEPATOR_RE = re.compile(
    r"""
            # regex to match the zero-width pattern in the middle of "]["
            (?<= # look-behind
                \] # literal ]
            )
            (?= # look-ahead
                \[ # literal [
            )
           """,
    re.VERBOSE,
)


def split_brackets(s):
    if s == "":
        return []
    return _BRACKET_SEPATOR_RE.split(s)


class ParadigmManagerWithExplicitSizes(ParadigmManager):
    """
    A ParadigmManager but its sizes are always returned, sorted according the explicit
    order specified.
    """

    def __init__(
        self,
        layout_directory: Path,
        generation_fst: Transducer,
        *,
        ordered_sizes: list[str],
    ):
        super().__init__(layout_directory, generation_fst)
        self._size_to_order = {
            element: index for index, element in enumerate(ordered_sizes)
        }

    def sizes_of(self, paradigm_name: str) -> Collection[str]:
        unsorted_results = super().sizes_of(paradigm_name)
        if len(unsorted_results) <= 1:
            return unsorted_results
        return sorted(unsorted_results, key=self._sort_by_explict_order)

    def _sort_by_explict_order(self, element: str) -> int:
        """
        Orders elements according to the given ordered sizes.
        Can be used as a key function for sort() or sorted().
        """
        return self._size_to_order[element]

    def all_sizes_fully_specified(self):
        """
        Returns True when all size options for all paradigms are specified in the
        explicit order given in the constructor.
        """
        valid_sizes = {ONLY_SIZE} | self._size_to_order.keys()
        all_paradigms = self._name_to_layout.keys()

        for paradigm in all_paradigms:
            # use super() to avoid any ordering stuff.
            sizes_available = super().sizes_of(paradigm)
            for size in sizes_available:
                if size not in valid_sizes:
                    logger.error(
                        "Paradigm %r has a layout in size %r, however that "
                        "size has not been declared",
                        paradigm,
                        size,
                    )
                    return False

        return True


def _load_all_layouts_in_directory(path: Path):
    """
    Yields (paradigm, size, layout) tuples from the given directory. Immediate
    subdirectories are assumed to be paradigms with multiple size options.
    """
    assert path.is_dir()

    for filename in path.iterdir():
        if filename.is_dir():
            yield from _load_all_sizes_for_paradigm(filename)
        elif filename.match("*.tsv"):
            yield filename.stem, ONLY_SIZE, _load_layout_file(filename)


def _load_all_sizes_for_paradigm(directory: Path):
    """
    Yields (paradigm, size, layout) tuples for ONE paradigm name. The paradigm name
    is inferred from the directory name.
    """
    paradigm_name = directory.name
    assert directory.is_dir()

    for layout_file in directory.glob("*.tsv"):
        size = layout_file.stem
        assert size != ONLY_SIZE, f"size name cannot clash with sentinel value: {size}"
        yield paradigm_name, size, _load_layout_file(layout_file)


def _load_layout_file(layout_file: Path):
    return ParadigmLayout.loads(layout_file.read_text(encoding="UTF-8"))


class Transducer(Protocol):
    """
    Interface for something that can lookup forms in bulk.

    This is basically the subset of the hfst_optimized_lookup.TransducerFile API that
    the paradigm manager actually uses.
    """

    def bulk_lookup(self, strings: Iterable[str]) -> dict[str, set[str]]: ...

from pathlib import Path
from typing import TypedDict

from morphodict.utils.serializer import SerializedSearchResult


class SearchResult(TypedDict):
    time_taken_seconds: float
    results: list[SerializedSearchResult]


SampleSearchResultsJson = dict[str, SearchResult]


RESULTS_DIR = Path(__file__).parent / "sample_results"
DEFAULT_SAMPLE_FILE = Path(__file__).parent / "sample.csv"

SURVEY_DIR = Path(__file__).parent / "survey_results"

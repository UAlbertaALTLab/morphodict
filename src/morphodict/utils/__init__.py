from .cree_lev_dist import get_modified_distance  # Unused but exported
from .shared_res_dir import shared_res_dir        # Unused but exported
from urllib.parse import ParseResult, urlencode, urlunparse

from django.urls import reverse
import requests
import urllib

def url_for_query(user_query: str) -> str:
    """
    Produces a relative URL to search for the given user query.
    """
    parts = ParseResult(
        scheme="",
        netloc="",
        params="",
        path=reverse("cree-dictionary-search"),
        query=urlencode((("q", user_query),)),
        fragment="",
    )
    return urlunparse(parts)


def get_recordings_from_url(search_terms, url, speech_db_eq):
    matched_recordings = {}
    query_params = [("q", term) for term in search_terms]
    response = requests.get(url + "?" + urllib.parse.urlencode(query_params))
    recordings = response.json()

    for recording in recordings["matched_recordings"]:
        if "moswacihk" in speech_db_eq:
            entry = macron_to_circumflex(recording["wordform"])
        else:
            entry = recording["wordform"]
        matched_recordings[entry] = {}
        matched_recordings[entry]["recording_url"] = recording["recording_url"]
        matched_recordings[entry]["speaker"] = recording["speaker"]

    return matched_recordings


def macron_to_circumflex(item):
    """
    >>> macron_to_circumflex("wāpamēw")
    'wâpamêw'
    """
    item = item.translate(str.maketrans("ēīōā", "êîôâ"))
    return item
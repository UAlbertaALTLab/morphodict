from __future__ import annotations
#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Utilities that depend on the CreeDictionary Django application.
"""

from urllib.parse import ParseResult, urlencode, urlunparse

import urllib
import logging
import paradigm_panes
from typing import Optional

import requests
from django.conf import settings

from CreeDictionary.CreeDictionary.paradigm.generation import default_paradigm_manager
from crkeng.app.preferences import DictionarySource
from morphodict.lexicon.models import Wordform

from CreeDictionary.CreeDictionary.paradigm.panes import Paradigm
from CreeDictionary.morphodict.templatetags.morphodict_orth import ORTHOGRAPHY

from utils.shared_res_dir import shared_res_dir


from django.urls import reverse

logger = logging.getLogger(__name__)


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


def get_dict_source(request):
    """
    Returns a dictionary source given a request.

    If a paradigm cannot be found, None is returned

    :param request:
    :return:
    """
    if dictionary_source := DictionarySource.current_value_from_request(request):
        if dictionary_source:
            ret = dictionary_source.split("+")
            ret = [r.upper() for r in ret]
            return ret
    return None


def paradigm_for(wordform: Wordform, paradigm_size: str) -> Optional[Paradigm]:
    """
    Returns a paradigm for the given wordform at the desired size.

    If a paradigm cannot be found, None is returned

    :param wordform:
    :param paradigm_size:
    :return:
    """
    fst_dir = settings.BASE_DIR / "resources" / "fst" / settings.STRICT_GENERATOR_FST_FILENAME
    layout_dir = shared_res_dir / "layouts"
    site_specific_layout_dir = settings.BASE_DIR / "resources" / "layouts"
    if site_specific_layout_dir.exists():
        layout_dir = site_specific_layout_dir

    pg = paradigm_panes.PaneGenerator()
    pg.set_layouts_dir(layout_dir)
    pg.set_fst_filepath(fst_dir)

    manager = default_paradigm_manager()

    if name := wordform.paradigm:
        fst_lemma = wordform.lemma.text

        if settings.MORPHODICT_ENABLE_FST_LEMMA_SUPPORT:
            fst_lemma = wordform.lemma.fst_lemma

        if paradigm := pg.generate_pane(fst_lemma, name, paradigm_size):
            return paradigm
        logger.warning(
            "Could not retrieve static paradigm %r " "associated with wordform %r",
            name,
            wordform,
        )

    return None


def get_recordings_from_paradigm(paradigm, request):
    """
    Returns a recordings given a paradigm and request.

    :param paradigm:
    :param request:
    :return:
    """
    if request.COOKIES.get("paradigm_audio") == "no":
        return paradigm

    query_terms = []
    matched_recordings = {}
    speech_db_eq = settings.SPEECH_DB_EQ
    url = f"https://speech-db.altlab.app/{speech_db_eq}/api/bulk_search"
    synth_url = "https://speech-db.altlab.app/synth/api/bulk_search"

    for pane in paradigm["panes"]:
        for row in pane["tr_rows"]:
            if not row["is_header"]:
                for cell in row["cells"]:
                    if cell["is_inflection"] and not cell["is_missing"]:
                        query_terms.append(cell["inflection"])

    for search_terms in divide_chunks(query_terms, 30):
        matched_recordings.update(get_recordings_from_url(search_terms, synth_url))
        matched_recordings.update(get_recordings_from_url(search_terms, url))

    for pane in paradigm["panes"]:
        for row in pane["tr_rows"]:
            if not row["is_header"]:
                for cell in row["cells"]:
                    if cell["is_inflection"] and not cell["is_missing"]:
                        if cell["inflection"] in matched_recordings:
                            cell["recording"] = matched_recordings[cell["inflection"]]

    return paradigm


def get_recordings_from_url(search_terms, url):
    """
    Iterate through the recordings and chooses the matched recordings. Returns recordings given search terms and url.

    :param search_terms:
    :param string:
    :return:
    """
    matched_recordings = {}
    query_params = [("q", term) for term in search_terms]
    response = requests.get(url + "?" + urllib.parse.urlencode(query_params))
    recordings = response.json()

    for recording in recordings["matched_recordings"]:
        matched_recordings[recording["wordform"]] = recording["recording_url"]

    return matched_recordings


# Consider moving function the contents of this function to presentation.serialize_wordform
def wordform_orth(wordform):
    """
    Modifies a serialized wordform object. The text and inflectional_catagory_plain_english fields are modifed to
    contain a dictionary containing all orthographic representations of their text given in Standard Roman Orthography.

    e.g.,

        'wâpamêw'

    becomes:

        {
            "Latn": "wâpamêw",
            "Latn-x-macron": "wāpamēw",
            "Cans": "ᐚᐸᒣᐤ"
        }

    :param wordform:
    :return:
    """
    try:
        wordform["text"] = {
            code: ORTHOGRAPHY.converter[code](wordform["text"])
            for code in ORTHOGRAPHY.available
        }
        wordform["inflectional_category_plain_english"] = {
            code: "like: " + ORTHOGRAPHY.converter[code](wordform["inflectional_category_plain_english"][6:])
            for code in ORTHOGRAPHY.available
        }

    except TypeError:
        wordform["text"] = {"Latn": wordform["text"]}
        wordform["inflectional_category_plain_english"] = {"Latn": wordform["inflectional_category_plain_english"]}

    return wordform


def paradigm_orth(paradigm):
    """
    Modifies inflections in a serialized paradigm to include all orthographic representations
    """
    print(paradigm)
    for pane in paradigm["panes"]:
        for row in pane["tr_rows"]:
            try:
                for cell in row["cells"]:
                    if cell["is_inflection"] and not cell["is_missing"]:
                        cell["inflection"] = orth(cell["inflection"])
            except NotImplementedError as e:
                logger.error("No cells for row:", e)
    return paradigm


def orth(word):
    """
    Returns a dictionary containing all orthographic representations of a word given in
    Standard Roman Orthography.

    e.g.,

        'wâpamêw'

    Returns:

        {
            "Latn": "wâpamêw",
            "Latn-x-macron": "wāpamēw",
            "Cans": "ᐚᐸᒣᐤ"
        }

    :param word: a word given in SRO with macrons as circumflex
    :return:
    """
    try:
        return {
            code: ORTHOGRAPHY.converter[code](word)
            for code in ORTHOGRAPHY.available
        }
    except TypeError:
        return {"Latn": word}


# Yield successive n-sized
# chunks from l.
# https://www.geeksforgeeks.org/break-list-chunks-size-n-python/
def divide_chunks(terms, size):
    # looping till length l
    for i in range(0, len(terms), size):
        yield terms[i: i + size]

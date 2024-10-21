from morphodict.utils import get_recordings_from_url
from morphodict.paradigm.panes import WordformCell

def get_recordings_from_paradigm(paradigm, paradigm_audio: bool, speech_db_eq: list[str]):
    if not paradigm_audio:
        return paradigm

    query_terms = []
    matched_recordings = {}

    for pane in paradigm.panes:
        for row in pane.tr_rows:
            if not row.is_header:
                for cell in row.cells:
                    if cell.is_inflection:
                        query_terms.append(str(cell))

    for search_terms in divide_chunks(query_terms, 30):
        for source in speech_db_eq:
            url = f"https://speech-db.altlab.app/{source}/api/bulk_search"
            matched_recordings.update(
                get_recordings_from_url(search_terms, url, speech_db_eq)
            )

    for pane in paradigm.panes:
        for row in pane.tr_rows:
            if not row.is_header:
                for cell in row.cells:
                    if cell.is_inflection and isinstance(cell, WordformCell):
                        if cell.inflection in matched_recordings.keys():
                            cell.add_recording(matched_recordings[str(cell)])

    return paradigm


# Yield successive n-sized
# chunks from l.
# https://www.geeksforgeeks.org/break-list-chunks-size-n-python/
def divide_chunks(terms, size):
    # looping till length l
    for i in range(0, len(terms), size):
        yield terms[i : i + size]
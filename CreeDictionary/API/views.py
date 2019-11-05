from django.http import JsonResponse


# todo: update api documentation


def translate_cree(request, query_string: str) -> JsonResponse:
    """
    click-in-text api

    note: returned definition is for lemma, not the queried inflected form.
    see https://github.com/UAlbertaALTLab/cree-intelligent-dictionary/wiki/Web-API for API specifications
    """
    # todo (for matt): rewrite this
    pass

from morphodict import morphodict_language_pair


def language_pair(request):
    return {"LANGUAGE_PAIR": morphodict_language_pair()}

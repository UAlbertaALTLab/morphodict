from django.urls import path

from morphodict.paradigm import views


urlpatterns = [
    # internal use to render paradigm and only the paradigm
    path(
        "_paradigm_details/",
        views.paradigm_internal,
        name="morphodict-paradigm-detail",
    ),
    path(
        "api/paradigm_layout/html",
        views.paradigm_for_lemma,
        name="morphodict-paradigm-layout",
    ),
    path(
        "api/paradigm_layout/json",
        views.json_paradigm_for_lemma,
        name="morphodict-json-paradigm-layout",
    ),
]

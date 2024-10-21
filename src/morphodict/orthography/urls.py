from django.urls import path

from . import views

app_name = "morphodict.orthography"
urlpatterns = [
    path(
        "change-orthography",
        views.ChangeOrthography.as_view(),
        name="change-orthography",
    ),
]

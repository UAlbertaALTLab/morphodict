from django.urls import path

from . import views

app_name = "morphodict"
urlpatterns = [
    path(
        "change-orthography",
        views.ChangeOrthography.as_view(),
        name="change-orthography",
    ),
]

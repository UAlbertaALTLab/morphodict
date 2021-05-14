from django.urls import path, re_path

from . import views

app_name = "search_quality"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    re_path(
        # the strict regex is to prevent directory traversal attacks
        r"^analyze/(?P<path>[a-zA-Z0-9_-]+\.json\.gz)$",
        views.ResultsAnalysisView.as_view(),
        name="results-analysis",
    ),
    path("run", views.run, name="run-analysis"),
]

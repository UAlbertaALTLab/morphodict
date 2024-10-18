from django.urls import path
import morphodict.api.views as api_views

################################ Click in text #################################
# cree word translation for click-in-text
urlpatterns = [
    path(
        "click-in-text/",
        api_views.click_in_text,
        name="cree-dictionary-word-click-in-text-api",
    ),
    path(
        "click-in-text-embedded-test/",
        api_views.click_in_text_embedded_test,
        name="cree-dictionary-click-in-text-embedded-test",
    ),
]

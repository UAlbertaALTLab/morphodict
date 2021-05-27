from http import HTTPStatus

from django.http import HttpResponse
from django.views import View

PARADIGM_LABEL_COOKIE = "paradigmlabel"
PARADIGM_LABEL_OPTIONS = {"english", "linguistic", "nehiyawewin"}


class ChangeParadigmLabelPreference(View):
    """
    Sets the paradigmlabel= cookie, which affects the type of labels ONLY IN THE
    PARADIGMS!

        > POST /change-paradigm-label HTTP/1.1
        > Referer: /word/minôs
        > Cookie: paradigmlabel=english
        >
        > paradigmlabel=nehiyawewin

        < HTTP/1.1 302 See Other
        < Set-Cookie: paradigmlabel=nehiyawewin
        < Location: /word/minôs

    """

    def post(self, request) -> HttpResponse:
        label = request.POST.get(PARADIGM_LABEL_COOKIE)

        # Tried to set to an unknown display mode
        if label not in PARADIGM_LABEL_OPTIONS:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)

        if who_asked_us := request.headers.get("Referer"):
            # Force the browser to refresh the page that issued this request.
            response = HttpResponse(status=HTTPStatus.SEE_OTHER)
            response.headers["Location"] = who_asked_us
        else:
            # We don't know where to redirect, so send no content.
            # (also, this probably should never happen?)
            response = HttpResponse(status=HTTPStatus.NO_CONTENT)

        response.set_cookie(PARADIGM_LABEL_COOKIE, label)
        return response

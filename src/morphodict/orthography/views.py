#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from http import HTTPStatus

from django.http import HttpResponse
from django.views import View

from .orthography import ORTHOGRAPHY


class ChangeOrthography(View):
    """
    Sets the orth= cookie, which affects the default rendered orthography.

        > POST /change-orthography HTTP/1.1
        > Cookie: orth=Latn
        >
        > orth=Cans

        < HTTP/1.1 204 No Content
        < Set-Cookie: orth=Cans

    Supports only POST requests for now.
    """

    def post(self, request):
        orth = request.POST.get("orth")

        # Tried to set to an unsupported orthography
        if orth not in ORTHOGRAPHY.available:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)

        response = HttpResponse(status=HTTPStatus.NO_CONTENT)
        response.set_cookie("orth", orth)
        return response

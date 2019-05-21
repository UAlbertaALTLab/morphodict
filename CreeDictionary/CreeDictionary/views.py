from django.http import HttpResponse
from django.urls import reverse


# the reason for *args: when re_path is used in urls.py, matched groups will be passed as extra positional arguments
def index(request, *args):
    return HttpResponse(str(reverse("cree-dictionary-index")))

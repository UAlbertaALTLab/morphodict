from .settings import *

STORAGES["staticfiles"] = {
    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
}
ALLOWED_HOSTS.append("127.0.0.1")

MORPHODICT_ENABLE_CVD = False
MORPHODICT_ENABLE_AFFIX_SEARCH = False

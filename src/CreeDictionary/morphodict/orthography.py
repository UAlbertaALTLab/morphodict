"""
Handling of the writing system of the language.
"""

import logging
from importlib import import_module
from typing import Callable, Set

from django.conf import settings
from django.http import HttpRequest

logger = logging.getLogger(__name__)


class Orthography:
    COOKIE_NAME = "orth"

    class _Converter:
        def __getitem__(self, code: str) -> Callable[[str], str]:
            path = settings.MORPHODICT_ORTHOGRAPHY["available"][code].get(
                "converter", None
            )
            if path is None:
                return lambda text: text

            *module_path, callable_name = path.split(".")
            module = import_module(".".join(module_path))
            return getattr(module, callable_name)

    converter = _Converter()

    @property
    def default(self) -> str:
        return settings.MORPHODICT_ORTHOGRAPHY["default"]

    @property
    def available(self) -> Set[str]:
        return set(settings.MORPHODICT_ORTHOGRAPHY["available"].keys())

    def name_of(self, code: str) -> str:
        """
        Get the plain English name of the given orthography code.
        """
        return settings.MORPHODICT_ORTHOGRAPHY["available"][code]["name"]

    def from_request(self, request: HttpRequest) -> str:
        """
        Return the requested orthography code from the HTTP request. If the request
        does not specify an orthography, the default code is returned.
        """

        orthography = request.COOKIES.get(self.COOKIE_NAME, self.default)

        # If the orthography cookie has an invalid value—often encountered when
        # doing development work that changes what orthographies are
        # available—then use the default orthography instead.
        if orthography not in self.available:
            logger.warning(
                f"Requested orthography {orthography!r} not found, using default instead"
            )
            orthography = ORTHOGRAPHY.default
            # This doesn’t actually set the cookie, as that would have to happen
            # on the Response object, which likely hasn’t been created yet, or
            # in some middleware; but it at least prevents the same warning from
            # being logged repeatedly for the same request.
            request.COOKIES[self.COOKIE_NAME] = orthography

        return orthography


ORTHOGRAPHY = Orthography()

"""
Handling of the writing system of the language.
"""

from importlib import import_module
from typing import Callable, Set

from django.conf import settings
from django.http import HttpRequest


class Orthography:
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
        return request.COOKIES.get("orth", self.default)


ORTHOGRAPHY = Orthography()

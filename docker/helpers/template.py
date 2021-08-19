"""
Convenience functions for using Django’s template system outside of a
traditional Django app.
"""

# functools.cache was added in 3.9, and the system python may be older.
try:
    from functools import cache as cache_if_available
except ImportError:

    def cache_if_available(func):
        return func


@cache_if_available
def get_engine():
    # This import is nested so that all other commands for the program can run
    # even if Django is not installed.
    from django.template import Engine

    # Raise an error if a template refers to a nonexistent variable. Inspired by
    # https://stackoverflow.com/a/15312316/14558
    class InvalidVariableReference:
        """
        A reference to an invalid variable, arising from a Django template.
        Raises an exception when used.
        """

        def _error_out(self):
            raise Exception("this should not get called")

        def __contains__(self, item):
            if item == "%s":
                return True
            self._error_out()

        def __mod__(self, other):
            raise Exception(f"Invalid variable access: {other!r}")

        def __getattr__(self, item):
            self._error_out()

    return Engine(string_if_invalid=InvalidVariableReference())


def render_template(template_string, context_dict):
    # This import is nested so that all other commands for the program can run
    # even if Django is not installed.
    from django.template import Template, Context

    template = Template(template_string, engine=get_engine())
    context = Context(context_dict, use_l10n=False)
    return template.render(context)

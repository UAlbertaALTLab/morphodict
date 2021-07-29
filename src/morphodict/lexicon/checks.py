from django.core.checks import Error, register
from django.conf import settings


@register()
def check_settings(**kwargs):
    errors = []

    # if 'FOO' not in settings:
    #     errors.append(Error('Required setting FOO not set.'))

    return errors


def register_checks():
    """
    This function doesn’t do anything by itself, but by calling it from the
    top-level of models.py, we ensure that the @register() decorators above run.
    """

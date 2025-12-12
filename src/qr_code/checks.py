"""
Checks done at startup.
"""

from django.core.checks import register

from .common.environment import get_environment


@register()
def check_environment(*args, **kwargs):
    _, errors = get_environment()
    return errors

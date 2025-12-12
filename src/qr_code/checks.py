"""
Checks done at startup.
"""

from django.core.checks import register

from .common.environment import get_environment


@register()
def check_environment(*args, **kwargs):
    _, checks = get_environment()
    return checks

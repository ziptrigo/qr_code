"""
Checks done at startup.
"""

from django.conf import settings
from django.core.checks import Error, register

from .common.environment import get_environment
from .services.email_service import (
    EMAIL_BACKEND_KIND_TO_CLASS,
    parse_email_backend_kinds,
)


@register()
def check_environment(*args, **kwargs):
    _, checks = get_environment()

    raw_backends = getattr(settings, 'EMAIL_BACKENDS', '')
    kinds = parse_email_backend_kinds(raw_backends)

    if not kinds:
        checks.append(
            Error(
                'EMAIL_BACKENDS must be set to a comma-separated list of backend kinds.',
                hint='Example: EMAIL_BACKENDS=console or EMAIL_BACKENDS=ses,console',
                id='E010',
            )
        )
        return checks

    unknown = [k for k in kinds if k not in EMAIL_BACKEND_KIND_TO_CLASS]
    if unknown:
        checks.append(
            Error(
                f'Unknown EMAIL_BACKENDS kind(s): {unknown}',
                hint=f'Valid kinds: {sorted(EMAIL_BACKEND_KIND_TO_CLASS.keys())}',
                id='E011',
            )
        )

    return checks

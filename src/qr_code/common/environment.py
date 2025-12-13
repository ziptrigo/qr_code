import os

from django.core.checks import CheckMessage, Error, Info, Warning

from .env_selection import SUPPORTED_ENVIRONMENTS, select_env
from .. import PROJECT_ROOT


def get_environment() -> tuple[str | None, list[CheckMessage]]:
    """
    Get the current environment from the ``ENVIRONMENT`` environment variable
    or try to deduce it from the ``.env`` file at the root of the project.

    Note: Sets the ``ENVIRONMENT`` environment variable.
    """
    selection = select_env(PROJECT_ROOT)

    checks: list[CheckMessage] = []

    if selection.environment in SUPPORTED_ENVIRONMENTS:
        checks.append(
            Info(
                f'ENVIRONMENT set to `{selection.environment}`.',
                id='I001',
            )
        )

    if selection.warnings:
        checks.append(
            Warning(
                '\n\n'.join(selection.warnings),
                hint='Either rename/remove the file(s), or add support for the environment.',
                id='W001',
            )
        )

    if selection.errors:
        # Preserve old error IDs for compatibility with existing expectations.
        if any('ENVIRONMENT environment variable' in e for e in selection.errors):
            checks.append(
                Error(
                    '\n'.join(selection.errors),
                    hint=f'Valid environments: {SUPPORTED_ENVIRONMENTS}',
                    id='E001',
                )
            )
        elif any('More than one environment file' in e for e in selection.errors):
            checks.append(
                Error(
                    '\n'.join(selection.errors),
                    hint='Have only one `.env.<env>` file or set the `ENVIRONMENT` variable.',
                    id='E003',
                )
            )
        else:
            checks.append(
                Error(
                    '\n'.join(selection.errors),
                    hint='Create one `.env.<env>` file or set the `ENVIRONMENT` variable.',
                    id='E002',
                )
            )

    if selection.environment:
        os.environ['ENVIRONMENT'] = str(selection.environment).lower()

    return selection.environment, checks

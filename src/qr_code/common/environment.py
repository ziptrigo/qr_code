import os
from pathlib import Path

from django.core.checks import CheckMessage, Error, Info, Warning

from .. import PROJECT_ROOT

ENVIRONMENTS = ['dev', 'prod']


def get_environment() -> tuple[str | None, list[CheckMessage]]:
    """
    Get the current environment from the ``ENVIRONMENT`` environment variable
    or try to deduce it from the ``.env`` file at the root of the project.
    """
    checks: list[CheckMessage] = []

    environment = os.getenv('ENVIRONMENT', '').lower()
    ignored_environments = ['example']  # No extension (ex `.env`) is also ignored

    if environment:
        if environment not in (ENVIRONMENTS + ignored_environments):
            checks.append(
                Error(
                    f'ENVIRONMENT environment variable `{os.getenv("ENVIRONMENT")}` must be one '
                    f'of {ENVIRONMENTS} (case insensitive).',
                    hint='Either set the proper environment, or don\'t set it at all.',
                    id='E001',
                )
            )
    else:

        def env_from_file(file: Path) -> str | None:
            return file.suffix.lower() if file.stem.lower() == '.env' else None

        # Environment not set, try to deduct
        env_files = set(PROJECT_ROOT.glob('env*'))
        ignored_files = {
            env
            for env_file in env_files
            if (env := env_from_file(env_file)) is None and env in ignored_environments
        }
        env_files -= ignored_files
        unknown_files = {
            env for env_file in env_files if (env := env_from_file(env_file)) not in ENVIRONMENTS
        }
        if unknown_files:
            checks.append(
                Warning(
                    f'Unknown environment file(s) found in `{PROJECT_ROOT}`: \n'
                    + '\n'.join(map(str, unknown_files)),
                    hint='Either set the proper environment, or remove the file(s).',
                    id='W001',
                )
            )
        env_files -= unknown_files

        if not env_files:
            checks.append(
                Error(
                    f'No environment file found in `{PROJECT_ROOT}`.',
                    hint='Have one environment file or set the `ENVIRONMENT` variable.',
                    id='E002',
                )
            )
        elif len(env_files) > 1:
            checks.append(
                Error(
                    f'More than one environment file found in `{PROJECT_ROOT}`: \n'
                    + '\n'.join(map(str, env_files)),
                    hint='Have only one environment file or set the `ENVIRONMENT` variable.',
                    id='E003',
                )
            )

    if environment:
        os.environ['ENVIRONMENT'] = environment
        checks.append(Info(f'ENVIRONMENT: {environment}'))
    else:
        environment = None  # type: ignore

    return environment, checks

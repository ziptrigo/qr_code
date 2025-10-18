#!python
"""
Python packages related tasks.
"""
import logging
import subprocess
from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer

logger = logging.getLogger(__name__)

app = typer.Typer(
    help=__doc__,
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode='markdown',
)


class Requirements(StrEnum):
    """
    Requirements files.

    Order matters as most operations with multiple files need ``requirements.txt`` to be processed
    first.
    Add new requirements files here.
    """

    MAIN = 'requirements'
    DEV = 'requirements-dev'


class RequirementsType(StrEnum):

    IN = 'in'
    OUT = 'txt'


PROJECT_ROOT = Path(__file__).parents[1]

REQUIREMENTS_TASK_HELP = {
    'requirements': '`.in` file. Full name not required, just the initial name after the dash '
    f'(ex. "{Requirements.DEV.name}"). For main file use "{Requirements.MAIN.name}". '
    f'Available requirements: {", ".join(Requirements)}.'
}


def _run(dry: bool, *args) -> subprocess.CompletedProcess | None:
    logger.info({' '.join(args)})

    if dry:
        return None

    try:
        return subprocess.run(args, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(e)
        raise typer.Exit(1)


def _get_requirements_file(
    requirements: str | Requirements, requirements_type: str | RequirementsType
) -> Path:
    """Return the full requirements file path."""
    if isinstance(requirements, str):
        try:
            reqs = Requirements[requirements.upper()]
        except ValueError:
            try:
                reqs = Requirements(requirements.lower())
            except ValueError:
                logger.error(f'`{requirements}` is an unknown requirements file.')
                raise typer.Exit(1)
    else:
        reqs = requirements

    if isinstance(requirements_type, str):
        reqs_type = RequirementsType(requirements_type.lstrip('.').lower())
    else:
        reqs_type = requirements_type

    base_path = PROJECT_ROOT
    if reqs_type == RequirementsType.IN:
        base_path /= 'requirements'
    return base_path / f'{reqs}.{reqs_type}'


def _get_requirements_files(
    requirements: list[str] | None, requirements_type: str | RequirementsType
) -> list[Path]:
    """Get full filename+extension and sort by the order defined in ``Requirements``"""
    requirements_files = list(Requirements) if requirements is None else requirements
    return [_get_requirements_file(r, requirements_type) for r in requirements_files]


@app.command(name='compile')
def pip_compile(
    requirements: Annotated[
        list[str] | None,
        typer.Argument(
            'Requirement file(s) to compile. If not set, all files are compiled.',
            show_default=False,
        ),
    ] = None
):
    """
    Compile requirements file(s).
    """
    for filename in _get_requirements_files(requirements, 'in'):
        _run(['pip-compile', filename])


@app.command(name='sync')
def pip_sync(
    requirements: Annotated[
        list[str] | None,
        typer.Argument(
            'Requirement file(s) to compile. If not set, all files are compiled.',
            show_default=False,
        ),
    ] = None
):
    """
    Synchronize environment with requirements file.
    """
    _run('pip-sync', *' '.join(map(str, _get_requirements_files(requirements, 'txt'))))


@app.command(name='package')
def pip_package(
    requirements: Annotated[str],
    package: Annotated[list[str], typer.Argument(help='One or more packages to upgrade.')],
):
    """
    Upgrade package.
    """
    packages = [p.strip() for p in package.split(',')]
    for filename in _get_requirements_files(requirements, 'in'):
        _run(
            ['pip-compile', '--upgrade-package', *' --upgrade-package '.join(packages), filename]
        )


def pip_upgrade(requirements):
    """
    Try to upgrade all dependencies to their latest versions.

    Use `pip-compile <filename> --upgrade-package <package>` to only upgrade one package.
    Ex `pip-compile requirements-def.in --upgrade-package safety`
    """
    for filename in _get_requirements_files(requirements, 'in'):
        _run(['pip-compile', '--upgrade', filename])


if __name__ == '__main__':
    app()

#!python
"""
Python packages related tasks.
"""
import logging
import subprocess
from enum import StrEnum
from pathlib import Path
from typing import Annotated, TypeAlias

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

RequirementsAnnotation: TypeAlias = Annotated[
    list[str] | None,
    typer.Argument(
        help='Requirement file(s) to compile. If not set, all files are compiled.\nValues can be '
        + ', '.join([f'`{x.name.lower()}`' for x in Requirements]),
        show_default=False,
    ),
]

DryAnnotation: TypeAlias = Annotated[
    bool,
    typer.Option(
        help='Show the command that would be run without running it.',
        show_default=False,
    ),
]


def _run(dry: bool, *args) -> subprocess.CompletedProcess | None:
    logger.info(' '.join(map(str, args)))

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
    if isinstance(requirements, Requirements):
        reqs = requirements
    else:
        try:
            reqs = Requirements[requirements.upper()]  # noqa
        except ValueError:
            try:
                reqs = Requirements(requirements.lower())
            except ValueError:
                logger.error(f'`{requirements}` is an unknown requirements file.')
                raise typer.Exit(1)

    if isinstance(requirements_type, RequirementsType):
        reqs_type = requirements_type
    else:
        reqs_type = RequirementsType(requirements_type.lstrip('.').lower())

    base_path = PROJECT_ROOT / 'admin'
    return base_path / f'{reqs}.{reqs_type}'


def _get_requirements_files(
    requirements: list[str | Requirements] | None, requirements_type: str | RequirementsType
) -> list[Path]:
    """Get full filename+extension and sort by the order defined in ``Requirements``"""
    requirements_files = list(Requirements) if requirements is None else requirements
    return [_get_requirements_file(r, requirements_type) for r in requirements_files]


@app.command(name='compile')
def pip_compile(
    requirements: RequirementsAnnotation = None,
    clean: Annotated[
        bool,
        typer.Option(
            help=f'Delete the existing requirements `{RequirementsType.OUT.value}` files, forcing '
            f'a clean compilation.'
        ),
    ] = False,
    dry: DryAnnotation = False,
):
    """
    Compile requirements file(s).
    """
    if clean and not dry:
        for filename in _get_requirements_files(requirements, RequirementsType.OUT):
            filename.unlink(missing_ok=True)

    dry_option = ['--dry-run'] if dry else []
    for filename in _get_requirements_files(requirements, RequirementsType.IN):
        _run(False, 'pip-compile', *dry_option, str(filename))


@app.command(name='sync')
def pip_sync(requirements: RequirementsAnnotation = None, dry: DryAnnotation = False):
    """
    Synchronize environment with requirements file.
    """
    _run(dry, 'pip-sync', *' '.join(map(str, _get_requirements_files(requirements, 'txt'))))


@app.command(name='package')
def pip_package(
    requirements: RequirementsAnnotation,
    packages: Annotated[
        list[str], typer.Option('--packages', '-p', help='One or more packages to upgrade.')
    ],
    dry: DryAnnotation = False,
):
    """
    Upgrade one or more packages.
    """
    for filename in _get_requirements_files(requirements, RequirementsType.IN):
        _run(
            dry, 'pip-compile', '--upgrade-package', *' --upgrade-package '.join(packages), filename
        )


@app.command(name='upgrade')
def pip_upgrade(requirements, dry: DryAnnotation = False):
    """
    Try to upgrade all dependencies to their latest versions.

    Equivalent to ``compile`` with ``--clean`` option.

    Use ``package`` to only upgrade individual packages,
    Ex ``pip package dev mypy flake8``.
    """
    for filename in _get_requirements_files(requirements, RequirementsType.IN):
        _run(dry, ['pip-compile', '--upgrade', filename])


if __name__ == '__main__':
    app()

#!/usr/bin/env python
"""
Python packages related tasks.
"""
import logging
import subprocess
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
PROJECT_ROOT = Path()
REQUIREMENTS_MAIN = 'main'
REQUIREMENTS_FILES = {
    REQUIREMENTS_MAIN: 'requirements',
    'dev': 'requirements-dev',
}
"""
Requirements files.
Order matters as most operations with multiple files need ``requirements.txt`` to be processed
first.
Add new requirements files here.
"""

REQUIREMENTS_TASK_HELP = {
    'requirements': '`.in` file. Full name not required, just the initial name after the dash '
    f'(ex. "dev"). For main file use "{REQUIREMENTS_MAIN}". Available requirements: '
    f'{", ".join(REQUIREMENTS_FILES)}.'
}


def _get_requirements_file(requirements: str, extension: str) -> str:
    """
    Return the full requirements file name (with extension).

    :param requirements: The requirements file to retrieve. Can be the whole filename
        (no extension), ex `'requirements-dev'` or just the initial portion, ex `'dev'`.
        Use `'main'` for the `requirements` file.
    :param extension: Requirements file extension. Can be either `'in'` or `'txt'`.
    """
    filename = REQUIREMENTS_FILES.get(requirements, requirements)
    if filename not in REQUIREMENTS_FILES.values():
        logger.error(f'`{requirements}` is an unknown requirements file.')
        raise typer.Exit(1)

    ext = extension.lstrip('.').lower()

    return f'{filename}.{extension.lstrip(".")}'


def _get_requirements_files(requirements: str | None, extension: str) -> list[str]:
    extension = extension.lstrip('.')
    if requirements is None:
        requirements_files = list(REQUIREMENTS_FILES)
    else:
        requirements_files = _csstr_to_list(requirements)

    # Get full filename+extension and sort by the order defined in `REQUIREMENTS_FILES`
    filenames = [
        _get_requirements_file(r, extension) for r in REQUIREMENTS_FILES if r in requirements_files
    ]

    return filenames


def pip_compile(requirements=None):
    """
    Compile requirements file(s).
    """
    for filename in _get_requirements_files(requirements, 'in'):
        subprocess.run(['pip-compile', filename], check=True)


def pip_sync(requirements=None):
    """
    Synchronize environment with requirements file.
    """
    subprocess.run('pip-sync', *' '.join(_get_requirements_files(requirements, 'txt')))


@task(
    help=REQUIREMENTS_TASK_HELP | {'package': 'Package to upgrade. Can be a comma separated list.'}
)
def pip_package(requirements, package):
    """
    Upgrade package.
    """
    packages = [p.strip() for p in package.split(',')]
    for filename in _get_requirements_files(requirements, 'in'):
        subprocess.run(
            ['pip-compile', '--upgrade-package', *' --upgrade-package '.join(packages), filename]
        )


def pip_upgrade(requirements):
    """
    Try to upgrade all dependencies to their latest versions.

    Use `pip-compile <filename> --upgrade-package <package>` to only upgrade one package.
    Ex `pip-compile requirements-def.in --upgrade-package safety`
    """
    for filename in _get_requirements_files(requirements, 'in'):
        subprocess.run(['pip-compile', '--upgrade', filename])


if __name__ == '__main__':
    app()

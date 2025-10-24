import subprocess
import sys
from enum import Enum
from typing import Annotated, TypeAlias

import typer

from admin.pip import logger

DryAnnotation: TypeAlias = Annotated[
    bool,
    typer.Option(
        help='Show the command that would be run without running it.',
        show_default=False,
    ),
]


class OS(str, Enum):
    """Operating System."""

    Linux = 'linux'
    MacOS = 'mac'
    Windows = 'win'


def get_os() -> OS:
    """
    Similar to ``sys.platform`` and ``platform.system()``, but less ambiguous by returning an Enum
    instead of a string.

    Doesn't make granular distinctions of linux variants, OS versions, etc.
    """
    if sys.platform == 'darwin':
        return OS.MacOS
    if sys.platform == 'win32':
        return OS.Windows
    return OS.Linux


def _run(dry: bool, *args) -> subprocess.CompletedProcess | None:
    logger.info(' '.join(map(str, args)))

    if dry:
        return None

    try:
        return subprocess.run(args, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(e)
        raise typer.Exit(1)

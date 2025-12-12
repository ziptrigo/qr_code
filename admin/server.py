#!python
"""
Run Django server.

Equivalent to ``python manage.py runserver``, just makes it easier to set the environment when
multiple environment files exist (which should be the case in development machines only).
"""
import os
import sys
from enum import Enum
from typing import Annotated

import typer

from admin.utils import DryAnnotation, logger, run


class Environment(Enum):
    DEV = 'dev'
    PROD = 'prod'


app = typer.Typer(
    help=__doc__,
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode='markdown',
)


@app.command(name='run')
def server_run(
    environment: Annotated[
        Environment, typer.Argument(help='Environment to start the server in.', show_default=True)
    ] = Environment.DEV,
    dry: DryAnnotation = False,
):
    """
    Run Django server.

    Equivalent to ``python manage.py runserver``, just makes it easier to set the environment when
    multiple environment files exist (which should be the case in development machines only).

    To use more options from ``manage.py``, use ``python manage.py runserver`` directly.
    Set the ``ENVIRONMENT`` environment variable to the desired environment.
    """
    from src.qr_code.common.environment import ENVIRONMENTS

    # Make sure the environment is valid (didn't change in the code)
    if environment.value not in ENVIRONMENTS:
        logger.error(
            f'Invalid environment: {environment.value}. Not defined in code: {ENVIRONMENTS}.'
        )
        raise typer.Exit(1)

    python_exe = sys.executable
    run(
        python_exe,
        'manage.py',
        'runserver',
        dry=dry,
        env=os.environ | {'ENVIRONMENT': environment.value},
    )


if __name__ == '__main__':
    app()

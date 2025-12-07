import os
import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from admin import PROJECT_ROOT
from admin.utils import logger

app = typer.Typer()


def setup_django(db_file: Path):
    """Configure Django settings to use the specified database file."""
    import django

    sys.path.insert(0, str(PROJECT_ROOT.resolve()))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    # Override database settings to use the specified file
    from django.conf import settings

    if not settings.configured:
        django.setup()
    else:
        settings.DATABASES['default']['NAME'] = db_file


@app.command(name='users')
def db_users(
    file: Annotated[Path, typer.Option(help='Path to the SQLite database file')] = Path(
        'db.sqlite3'
    ),
):
    """List all users from the database in a table format."""
    if not file.exists():
        logger.info(f'Database file not found: {file}')
        raise typer.Exit(1)

    setup_django(file)

    from src.qr_code.models import User

    users = User.objects.all()

    if not users:
        logger.warning('No users found in the database.')
        return

    table = Table(title='Users')
    table.add_column('ID', style='cyan', no_wrap=True)
    table.add_column('Username', style='magenta')
    table.add_column('Email', style='green')
    table.add_column('Name')
    table.add_column('Admin', justify='center')

    for user in users:
        table.add_row(
            str(user.id),
            user.username,
            user.email,
            user.name,
            'x' if user.is_staff else '',
        )

    console = Console()
    console.print(table)


if __name__ == '__main__':
    app()

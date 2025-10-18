#!python
"""
Project administration operations.
"""
from pathlib import Path

try:
    import typer
except ImportError:
    print(f'Required packages not installed.\nrun `{Path(__file__).name} install`.')
    raise SystemExit(1)

from admin import pip

app = typer.Typer(
    help=__doc__, no_args_is_help=True, add_completion=False, rich_markup_mode='markdown'
)

app.add_typer(pip.app, name='pip', no_args_is_help=True)

if __name__ == '__main__':
    app()

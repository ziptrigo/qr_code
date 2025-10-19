#!python
"""
Project administration operations.
"""
from pathlib import Path

try:
    import typer
    import piptools
except ImportError:
    print(f'Required packages not installed.\nrun `{Path(__file__).name} install`.')
    raise SystemExit(1)

from admin import pip

app = typer.Typer(
    help=__doc__, no_args_is_help=True, add_completion=False, rich_markup_mode='markdown'
)

app.add_typer(pip.app, name='pip', no_args_is_help=True)

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'install':
        # Handle install command
        import subprocess

        packages = ['typer', 'pip-tools']
        subprocess.run([sys.executable, '-m', 'pip', 'install', *packages], check=True)
        print('Main dependencies installed. Now installing remaining dependencies.')

        requirements = 'dev' if len(sys.argv) > 2 and sys.argv[2] == 'dev' else 'main'
        subprocess.run([sys.executable, '-m', 'admin.pip', 'sync', requirements], check=True)

        print('You can now run the admin commands. Use --help for more info.')
    else:
        app()

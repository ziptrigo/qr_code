#!python
"""
Generate OpenAPI specification.
"""
import json
import os
import sys
from enum import Enum
from pathlib import Path
from typing import Annotated

import typer

from admin import PROJECT_ROOT
from admin.utils import DryAnnotation, logger

app = typer.Typer(
    help=__doc__,
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode='markdown',
)


class Format(str, Enum):
    """Output format for OpenAPI specification."""

    json = 'json'
    yaml = 'yaml'


def setup_django():
    """Configure Django settings."""
    import django

    sys.path.insert(0, str(PROJECT_ROOT.resolve()))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    if not django.apps.apps.ready:
        django.setup()


@app.command(name='generate')
def generate_openapi(
    format: Annotated[
        Format,
        typer.Option(
            help='Output format for the OpenAPI specification.',
            case_sensitive=False,
        ),
    ] = Format.yaml,
    file: Annotated[
        Path | None,
        typer.Option(
            help='File path to save the specification. If not provided, ' 'displays on screen.',
            show_default=False,
        ),
    ] = None,
    dry: DryAnnotation = False,
):
    """
    Generate OpenAPI specification.

    Generates the OpenAPI schema in JSON or YAML format and optionally saves it to a file or
    displays it on the screen.
    """
    setup_django()

    from drf_spectacular.generators import SchemaGenerator

    try:
        logger.info(f'Generating OpenAPI schema in {format.value} format...')

        # Generate the schema
        generator = SchemaGenerator()
        schema = generator.get_schema()

        # Convert to desired format
        if format == Format.json:
            output = json.dumps(schema, indent=2)
        else:  # YAML
            try:
                import yaml
            except ImportError:
                logger.error(
                    'PyYAML is required for YAML output. ' 'Install it with: pip install pyyaml'
                )
                raise typer.Exit(1)

            output = yaml.dump(schema, default_flow_style=False, sort_keys=False)

        if dry:
            logger.info('DRY RUN: Schema generation successful')
            logger.info(f'Output format: {format.value}')
            if file:
                logger.info(f'Would save to: {file}')
            else:
                logger.info('Would display on screen')
            return

        # Save to file or display
        if file:
            file_path = Path(file)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(output)
            logger.info(f'OpenAPI schema saved to {file_path.resolve()}')
        else:
            # Display on screen
            print(output)
            logger.info('OpenAPI schema displayed on screen')

    except Exception as e:
        logger.error(f'Failed to generate OpenAPI schema: {e}')
        raise typer.Exit(1)


if __name__ == '__main__':
    app()

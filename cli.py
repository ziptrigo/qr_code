#!/usr/bin/env python
"""
QR Code CLI - Command line interface for QR code generation and management.

This CLI provides commands to interact with the QR code service.
"""

import os
from pathlib import Path
from typing import Optional

import requests
import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()

app = typer.Typer(help="QR Code Generator CLI")
console = Console()

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TOKEN_FILE = Path.home() / ".qrcode_token"


def get_token() -> Optional[str]:
    """Retrieve stored authentication token."""
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text().strip()
    return None


def save_token(token: str):
    """Save authentication token to file."""
    TOKEN_FILE.write_text(token)
    TOKEN_FILE.chmod(0o600)


def get_headers() -> dict:
    """Get headers with authentication token."""
    token = get_token()
    if not token:
        console.print("[red]Not authenticated. Please login first.[/red]")
        raise typer.Exit(1)
    return {"Authorization": f"Bearer {token}"}


@app.command()
def login(username: str, password: str):
    """
    Authenticate with the API and store the token.

    Example:
        qrcode login myuser mypassword
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/token/", json={"username": username, "password": password}
        )
        response.raise_for_status()
        token = response.json()["access"]
        save_token(token)
        console.print("[green]Successfully authenticated![/green]")
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Login failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def create(
    url: Optional[str] = typer.Option(None, "--url", "-u", help="URL to encode"),
    data: Optional[str] = typer.Option(None, "--data", "-d", help="Data to encode"),
    format: str = typer.Option("png", "--format", "-f", help="Output format (png, svg, jpeg)"),
    size: int = typer.Option(10, "--size", "-s", help="QR code size scale"),
    error_correction: str = typer.Option(
        "M", "--error", "-e", help="Error correction level (L, M, Q, H)"
    ),
    border: int = typer.Option(4, "--border", "-b", help="Border size"),
    bg_color: str = typer.Option("white", "--bg-color", help="Background color"),
    fg_color: str = typer.Option("black", "--fg-color", help="Foreground color"),
    shorten: bool = typer.Option(False, "--shorten", help="Use URL shortening"),
):
    """
    Create a new QR code.

    Example:
        qrcode create --url https://example.com --shorten
        qrcode create --data "Hello World" --format svg
    """
    if not url and not data:
        console.print("[red]Error: Either --url or --data must be provided[/red]")
        raise typer.Exit(1)

    payload = {
        "qr_format": format,
        "size": size,
        "error_correction": error_correction,
        "border": border,
        "background_color": bg_color,
        "foreground_color": fg_color,
        "use_url_shortening": shorten,
    }

    if url:
        payload["url"] = url
    else:
        payload["data"] = data

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/qrcodes/", json=payload, headers=get_headers()
        )
        response.raise_for_status()
        result = response.json()

        console.print("[green]QR Code created successfully![/green]")
        console.print(f"ID: {result['id']}")
        if result.get('short_code'):
            console.print(f"Short URL: {API_BASE_URL}/go/{result['short_code']}/")

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Failed to create QR code: {e}[/red]")
        if e.response is not None and hasattr(e.response, 'text'):
            console.print(f"[red]{e.response.text}[/red]")
        raise typer.Exit(1)


@app.command()
def list():
    """
    List all QR codes for the authenticated user.

    Example:
        qrcode list
    """
    try:
        response = requests.get(f"{API_BASE_URL}/api/qrcodes/", headers=get_headers())
        response.raise_for_status()
        qrcodes = response.json()

        if not qrcodes:
            console.print("[yellow]No QR codes found[/yellow]")
            return

        table = Table(title="Your QR Codes")
        table.add_column("ID", style="cyan")
        table.add_column("Content", style="white")
        table.add_column("Format", style="green")
        table.add_column("Scans", style="magenta")
        table.add_column("Created", style="blue")

        for qr in qrcodes:
            content = qr['content'][:50] + "..." if len(qr['content']) > 50 else qr['content']
            table.add_row(
                str(qr['id'])[:8],
                content,
                qr['qr_format'],
                str(qr['scan_count']),
                qr['created_at'][:10],
            )

        console.print(table)

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Failed to list QR codes: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def get(qr_id: str):
    """
    Get details of a specific QR code.

    Example:
        qrcode get abc123...
    """
    try:
        response = requests.get(f"{API_BASE_URL}/api/qrcodes/{qr_id}/", headers=get_headers())
        response.raise_for_status()
        qr = response.json()

        console.print(f"[cyan]ID:[/cyan] {qr['id']}")
        console.print(f"[cyan]Content:[/cyan] {qr['content']}")
        console.print(f"[cyan]Format:[/cyan] {qr['qr_format']}")
        console.print(f"[cyan]Size:[/cyan] {qr['size']}")
        console.print(f"[cyan]Scans:[/cyan] {qr['scan_count']}")
        console.print(f"[cyan]Image URL:[/cyan] {qr.get('image_url', 'N/A')}")
        if qr.get('redirect_url'):
            console.print(f"[cyan]Redirect URL:[/cyan] {qr['redirect_url']}")
        console.print(f"[cyan]Created:[/cyan] {qr['created_at']}")

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Failed to get QR code: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def delete(qr_id: str):
    """
    Delete a QR code.

    Example:
        qrcode delete abc123...
    """
    try:
        response = requests.delete(f"{API_BASE_URL}/api/qrcodes/{qr_id}/", headers=get_headers())
        response.raise_for_status()
        console.print(f"[green]QR code {qr_id} deleted successfully[/green]")

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Failed to delete QR code: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

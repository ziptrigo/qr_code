# QR Code Generator Service

A complete QR code generation and management service with Django REST API, JWT authentication, URL shortening, and CLI interface.

## Features

- 🎨 **Full Customization**: Colors, size, error correction, border, and multiple formats (PNG, SVG, PDF)
- 🔗 **URL Shortening**: Built-in URL shortener with redirect tracking
- 📊 **Analytics**: Track scan counts and timestamps
- 🔐 **JWT Authentication**: Secure API access
- 💻 **CLI Interface**: Command-line tool for all operations
- 🗄️ **Database Flexible**: SQLite for development, PostgreSQL-ready for production
- 🖼️ **Transparency Support**: PNG with transparent backgrounds

## Quick Start

```powershell
# Install dependencies
.venv313\Scripts\Activate.ps1
pip install -r requirements.txt

# Setup database
python manage.py migrate
python manage.py createsuperuser

# Create media directory
New-Item -ItemType Directory -Force -Path media\qrcodes

# Run server
python manage.py runserver
```

## Documentation

See [SETUP.md](SETUP.md) for complete installation, configuration, and usage instructions.

## API Endpoints

- `POST /api/token/` - Authenticate and get JWT token
- `POST /api/qrcodes/` - Create QR code
- `GET /api/qrcodes/` - List QR codes
- `GET /api/qrcodes/{id}/` - Get QR code details
- `DELETE /api/qrcodes/{id}/` - Delete QR code
- `GET /go/{short_code}/` - Redirect and track (public)

## Development

- Sort imports: `isort .`
- Format code: `black .`

## CLI Usage

```powershell
# Login
python cli.py login username password

# Create QR code
python cli.py create --url https://example.com --shorten

# List QR codes
python cli.py list
```

## Tech Stack

- **Backend**: Django 5.2 + Django REST Framework
- **Authentication**: JWT (Simple JWT)
- **QR Generation**: segno
- **CLI**: typer
- **Database**: SQLite (PostgreSQL-ready)
- **Tooling**: pytest, pytest-cov, black, isort

## License

MIT

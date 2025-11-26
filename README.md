[![Project License - MIT](https://img.shields.io/pypi/l/hd_active.svg)](https://github.com/joaonc/qr_code/blob/main/LICENSE.txt)

# QR Code Generator Service

A complete QR code generation and management service with Django REST API, session-based authentication, URL shortening, and CLI interface.

## Features

- 🎨 **Full Customization**: Colors, size, error correction, border, and multiple formats (PNG, SVG, PDF)
- 🔗 **URL Shortening**: Built-in URL shortener with redirect tracking
- 📊 **Analytics**: Track scan counts and timestamps
- 🔐 **Session Authentication**: Secure API access with session-based auth
- 💻 **CLI Interface**: Command-line tool for all operations
- 🗄️ **Database Flexible**: SQLite for development, PostgreSQL-ready for production
- 🖼️ **Transparency Support**: PNG with transparent backgrounds

## Quick Start

### Windows
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

### Mac / Linux
```bash
# Create and activate virtual environment
python3.13 -m venv .venv313
source .venv313/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file (optional but recommended)
cp .env.example .env

# Setup database
python manage.py migrate
python manage.py createsuperuser

# Create media directory
mkdir -p media/qrcodes

# Run server
python manage.py runserver
```

## Documentation

See [SETUP.md](SETUP.md) for complete installation, configuration, and usage instructions.

## API Endpoints

- `POST /api/signup` - Create user account (email, name, password)
- `POST /api/login` - Authenticate with email and password
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
- **Authentication**: Session-based authentication
- **QR Generation**: segno
- **CLI**: typer
- **Database**: SQLite (PostgreSQL-ready)
- **Tooling**: pytest, pytest-cov, black, isort

## License

MIT

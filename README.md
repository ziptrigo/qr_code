[![Project License - MIT](https://img.shields.io/pypi/l/hd_active.svg)](https://github.com/joaonc/qr_code/blob/main/LICENSE.txt)

# QR Code Generator Service

A complete QR code generation and management service with Django REST API, session-based authentication, URL shortening, web dashboard, and CLI interface.

## Features

- 🎨 **Full Customization**: Colors, size, error correction, border, and multiple formats (PNG, SVG, PDF)
- 🔗 **URL Shortening**: Built-in URL shortener with redirect tracking
- 📊 **Analytics**: Track scan counts and timestamps
- 🔐 **Session Authentication**: Secure API access with session-based auth
- 🔑 **Forgot Password**: Email-based password reset with time-limited tokens
- 🖥️ **Web Dashboard**: Login/register flow, QR code listing with search and sort, and an interactive QR code generator page (preview + save)
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

See [setup.md](docs/setup.md) for complete installation, configuration, and usage instructions.

## API Endpoints

- `POST /api/signup` - Create user account (email, name, password)
- `POST /api/login` - Authenticate with email and password
- `POST /api/forgot-password` - Request a password reset email (always returns 200)
- `POST /api/reset-password` - Reset password using a valid token (`token`, `password`, `password_confirm`)
- `POST /api/qrcodes/` - Create QR code (supports `name`, formats PNG/SVG/PDF, colors, and optional URL shortening)
- `POST /api/qrcodes/preview` - Generate a QR code image for preview without saving it to the database
- `GET /api/qrcodes/` - List QR codes
- `GET /api/qrcodes/{id}/` - Get QR code details
- `DELETE /api/qrcodes/{id}/` - Delete QR code
- `GET /go/{short_code}/` - Redirect and track (public)

## Web UI

- `/` - Home page with project overview and logo
- `/login/` - Login form using htmx + session-based auth (includes "Forgot your password?" link)
- `/register/` - Registration form using htmx
- `/forgot-password/` - Request a reset link via email. After submit, a generic success message is shown
  regardless of whether the email exists
- `/reset-password/<token>/` - Enter a new password. Invalid or expired tokens show an expiry page with a link
  back to login
- `/dashboard/` - Authenticated dashboard listing the user’s QR codes with search and sort options
- `/qrcodes/new/` - QR code generator page with:
  - Name field
  - Text/URL textarea (up to 1000 characters)
  - Format dropdown (PNG, SVG, PDF)
  - "Generate short URL" checkbox
  - Preview button that calls `POST /api/qrcodes/preview` and shows a live QR image
  - Final "Generate QR code" button that saves via `POST /api/qrcodes/` and redirects back to the dashboard

### Password reset and email configuration

- `PASSWORD_RESET_TOKEN_TTL_HOURS` (default: 4) controls token validity window
- `EMAIL_BACKEND` can be `console` (dev) or `ses` (production)
- For SES, set `SES_REGION` and `SES_SENDER` in your environment or settings

### How to use the generator

1. Log in (or register) and go to the `/dashboard/` page.
2. Click the **Generate QR code** button on the right of the search bar to open `/qrcodes/new/`.
3. Fill in:
   - **Name** – a label to identify this QR code in your dashboard.
   - **Text / URL to encode** – any text up to 1000 characters. This can be plain text or a URL.
   - **Format** – choose between PNG, SVG or PDF.
   - *(Optional)* **Generate short URL** – when enabled and the content is a valid URL, the service will store the original URL and encode a shortened redirect URL in the QR code. If the content is not a URL, this option has no effect.
4. Click **Generate QR code preview** to see what the QR image will look like. This does **not** save anything yet.
5. When satisfied, click **Generate QR code**. The QR code is saved via the API and you are redirected back to `/dashboard/`, where the new entry appears in the list.

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

- **Backend**: [Django](https://www.djangoproject.com) + [Django REST Framework](https://www.django-rest-framework.org)
- **Frontend**: [htmx](https://htmx.org) + [Alpine.js](https://alpinejs.dev) + [Tailwind CSS](https://tailwindcss.com)
- **Authentication**: Session-based authentication
- **QR Generation**: [segno](https://github.com/heuer/segno/)
- **CLI**: typer
- **Database**: SQLite (MySQL / PostgreSQL ready)
- **Tooling**: [pytest](https://pytest.org), pytest-cov, black, isort

## License

[MIT](https://mit-license.org)

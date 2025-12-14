[![Project License - MIT](https://img.shields.io/pypi/l/hd_active.svg)](https://github.com/ziptrigo/qr_code/blob/main/LICENSE.txt)

# QR Code Generator Service

A complete QR code generation and management service with Django REST API, session-based authentication, URL shortening, web dashboard, and CLI interface.

## Features

- 🎨 **Full Customization**: Colors, size, error correction, border, and multiple formats (PNG, SVG, PDF)
- 🏷️ **QR Code Types**: Support for URL and TEXT types to categorize QR code content
- 🔗 **URL Shortening**: Built-in URL shortener with redirect tracking
- 📊 **Analytics**: Track scan counts and timestamps
- 🔐 **Session Authentication**: Secure API access with session-based auth
- 📧 **Email Confirmation**: New users must confirm their email before logging in (48-hour link validity)
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

### API Documentation

- `/api/schema/` - OpenAPI schema (supports `?format=json` or `?format=yaml`)
- `/api/docs/` - Interactive Swagger UI documentation

### Endpoints

- `POST /api/signup` - Create user account and send confirmation email (email, name, password)
- `POST /api/login` - Authenticate with email and password (requires confirmed email)
- `POST /api/resend-confirmation` - Resend email confirmation link (email)
- `POST /api/confirm-email` - Confirm email using token (token)
- `POST /api/forgot-password` - Request a password reset email (always returns 200)
- `POST /api/reset-password` - Reset password using a valid token (`token`, `password`, `password_confirm`)
- `POST /api/qrcodes/` - Create QR code (supports `name`, `qr_type` (url/text), formats PNG/SVG/PDF, colors, and optional URL shortening)
- `POST /api/qrcodes/preview` - Generate a QR code image for preview without saving it to the database
- `GET /api/qrcodes/` - List QR codes (excludes soft-deleted, includes `qr_type` field)
- `GET /api/qrcodes/{id}/` - Get QR code details (includes `qr_type` field)
- `PUT /api/qrcodes/{id}/` - Update QR code name (only the name field can be modified; `qr_type` is read-only)
- `PATCH /api/qrcodes/{id}/` - Partially update QR code name
- `DELETE /api/qrcodes/{id}/` - Soft delete QR code (marks as deleted without physical removal)
- `GET /go/{short_code}/` - Redirect and track (public, redirects to dashboard if QR code is deleted)

## Web UI

- `/` - Home page with project overview and logo
- `/login/` - Login form using htmx + session-based auth (includes "Forgot your password?" link)
- `/register/` - Registration form using htmx (sends confirmation email upon successful registration)
- `/confirm-email/<token>/` - Confirm email address using the token from the confirmation email
- `/confirm-email/success/` - Success page shown after email confirmation with Login button
- `/forgot-password/` - Request a reset link via email. After submit, a generic success message is shown
  regardless of whether the email exists
- `/reset-password/<token>/` - Enter a new password. Invalid or expired tokens show an expiry page with a link
  back to login
|- `/dashboard/` - Authenticated dashboard listing the user's QR codes with search and sort options (requires confirmed email)
  - Each QR code row includes a dropdown menu (three-dots icon) with actions:
    - **Edit** - Opens the edit page for that QR code
    - **Delete** - Opens a confirmation modal to soft delete the QR code
  - Account settings link in the header
|- `/account/` - Account settings page for authenticated users with:
  - **Profile Information** section: editable name and email, read-only username; changing email requires confirmation
  - **Change Password** section: current password verification with password strength validation (min 6 chars, 1 digit)
  - Password visibility toggle buttons for all password fields
  - Link back to dashboard
- `/qrcodes/create/` - QR code creation page with:
  - Name field
  - Text/URL textarea (up to 1000 characters)
  - Format dropdown (PNG, SVG, PDF)
  - "Generate short URL" checkbox
  - Preview button that calls `POST /api/qrcodes/preview` and shows a live QR image
  - Final "Save" button that saves via `POST /api/qrcodes/` and redirects back to the dashboard
- `/qrcodes/edit/{id}/` - QR code editing page with:
  - Name field (editable)
  - Text/URL display (read-only, grayed out)
  - QR code preview (existing image)
  - "Save" button that updates via `PUT /api/qrcodes/{id}/` and redirects back to the dashboard

### Email confirmation and password reset configuration

- `EMAIL_CONFIRMATION_TOKEN_TTL_HOURS` (default: 48) controls email confirmation link validity
- `PASSWORD_RESET_TOKEN_TTL_HOURS` (default: 4) controls password reset link validity
- `EMAIL_BACKENDS` is a comma-separated list of backend kinds (e.g. `console` for dev or `ses` for production)
- You can specify multiple backends and the service will send the same email through all of them
  (e.g. `EMAIL_BACKENDS=ses,console`)
- For SES, set `AWS_REGION` and `AWS_SES_SENDER` in your environment

### Registration and login flow

1. Users register via `/register/` or `POST /api/signup`
2. A confirmation email is sent with a link valid for 48 hours
3. Users must click the confirmation link before they can log in
4. If the link expires, users can request a new one via the expired confirmation page
5. Once confirmed, users can log in normally at `/login/`

### How to create a QR code

1. Register an account and confirm your email, then log in and go to the `/dashboard/` page.
2. Click the **Generate QR code** button on the right of the search bar to open `/qrcodes/create/`.
3. Fill in:
   - **Name** – a label to identify this QR code in your dashboard.
   - **Type** – select either **URL** (for web addresses) or **Text** (for plain text content).
   - **Text / URL to encode** – any text up to 1000 characters. This can be plain text or a URL.
   - **Format** – choose between PNG, SVG or PDF.
   - *(Optional)* **Generate short URL** – when enabled and the content is a valid URL, the service will store the original URL and encode a shortened redirect URL in the QR code. If the content is not a URL, this option has no effect.
4. Click **Preview** to see what the QR image will look like. This does **not** save anything yet.
5. When satisfied, click **Save**. The QR code is saved via the API and you are redirected back to `/dashboard/`, where the new entry appears in the list.

### How to edit a QR code

1. From the `/dashboard/` page, click the three-dots menu icon on the right side of any QR code row.
2. Select **Edit** from the dropdown menu to open `/qrcodes/edit/{id}/`.
3. Update the **Name** field as needed. The QR code type, content, and format cannot be changed (displayed as read-only).
4. Click **Save** to update the QR code name via the API. You'll be redirected back to `/dashboard/`.

### How to delete a QR code

1. From the `/dashboard/` page, click the three-dots menu icon on the right side of any QR code row.
2. Select **Delete** from the dropdown menu.
3. A confirmation modal will appear asking you to confirm the deletion.
4. Click **Delete** to permanently remove the QR code, or **Cancel** to keep it.
5. Deleted QR codes are soft-deleted (marked as deleted in the database) and will no longer appear in your dashboard or be accessible via the API.

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

# QR Code Generator Project

## Project Overview
A Python project for generating and manipulating QR codes.

## Goals
- Create a flexible QR code generation service
- Support main QR code format
- Provide API, CLI and programmatic interfaces

## Tech Stack
- Python 3.13
- Django 6.0 for API and web interface (session-based auth, htmx + Tailwind templates)
- typer for CLI interface
- segno package for QR code generation
- Email: SES in production, console backend in development
- RDBMS for data storage

## App name and project structure
The app name is `qr_code`.
The app code is located under `src/qr_code`.
All references should reflect this structure.
Database tables related to the app have the prefix `qr_code`.
Models are stored under `src/qr_code/models`, each model in its own file.
API views live under `src/qr_code/api`, services under `src/qr_code/services`, and HTML templates under `src/qr_code/templates`.

## Current Status
Initial version done. Testing functionality and fixing bugs.
- Authentication flow implemented with `/login/`, `/register/`, and `/logout/`.
- Email confirmation flow implemented: users must confirm email before login, 48-hour token validity,
  `/confirm-email/<token>/` for confirmation, resend functionality on expired links.
- Forgot password flow implemented: `/forgot-password/` (initiation), `/reset-password/<token>/` (HTML),
  `POST /api/forgot-password` and `POST /api/reset-password` endpoints with time-limited tokens and email.
- Dashboard `/dashboard/` lists the authenticated user's QR codes (search + sort).
  - Each QR code row has a dropdown menu (three-dots icon) with Edit and Delete actions.
  - Clear search button (X icon) to reset filtering.
- QR code creation/editing:
  - `/qrcodes/create/` page lets users preview and save new QR codes.
  - `/qrcodes/edit/<id>/` page lets users edit the name of existing QR codes (content is read-only).
  - Both pages use the same template (`qrcode_editor.html`) with conditional rendering.
- Soft delete implemented: QR codes are marked as deleted (not physically removed) and hidden from all interfaces.

## Next Steps
1. Test authentication endpoints including email confirmation.
2. Test QRCode endpoints with session auth.
3. Test forgot password and reset flows (token validity, expiry, single-use).
4. Test email confirmation flow (signup, confirmation, expiry, resend).
5. Test edit functionality (PUT endpoint, ownership validation, UI behavior).
6. Fix issues as needed.

## Notes
### Coding guidelines
- Use PEP8
- Use docstrings
- Use type hints. Type hints to use python 3.13 standards, ex. `str | None` instead of
  `Optional[str]` and `list[str]` instead of `List[str]`. Functions that don't return anything
  (or return `None`) should not have a return type hint.
- Use static type checking
- Use black
- Use isort
- Use flake8
- Use mypy
- Use single quotes for strings, except when triple quotes are necessary (ex: docstrings), in which
  case use double quotes
- Use 4 spaces for indentation
- Use 100 characters per line

### Frontend design and behavior preferences
Frontend design language is minimal with a green-gray color palette from `src/qr_code/static/images/logo_128x128.png`.
All pages support light/dark mode including login and register.
Form validation includes existence checks and email format validation before backend calls.
On valid login, redirect to the dashboard page.
Include a 'remember me' checkbox with corresponding behavior.
User-facing error messages are simple; developer-facing errors are verbose and technical.
CSS stack uses Tailwind.

The QR dashboard and editor follow this stack:
- `dashboard.html` shows the user's QR codes with search, clear search button, and a "Generate QR code" button.
  - Each row has a dropdown menu (three-dots icon) with Edit option.
- `qrcode_editor.html` handles both create and edit modes:
  - Create mode (`/qrcodes/create/`): name, text/URL, format (PNG/SVG/PDF), short URL toggle, preview, and save.
  - Edit mode (`/qrcodes/edit/<id>/`): editable name, read-only content display, QR preview, and save.
- Preview uses `POST /api/qrcodes/preview` (no DB row).
- Create saves via `POST /api/qrcodes/`, edit updates via `PUT /api/qrcodes/<id>/`.
- Both redirect back to `/dashboard/` after successful save.

### Documentation
Create documentation in MD format under the `docs` directory, all lowercased files.
Only README.md remains in the root directory, uppercased.

### Functionality
1. Create QR code
When creating a QR code, the user should be able to specify the following:
- QR code type (URL or TEXT) - required field to categorize the content
- QR code format
- QR code content
- QR code size
- QR code error correction level
- QR code border
- QR code background color
- QR code foreground color
- QR code logo
- QR code logo size
- QR code data
- If the data is a url, then the user should be able to select whether the
  QR code will have that exact url, or a shortened url. The shortened url
  should be generated using functionality in this project that will point to
  an api endpoint that will then retrieve the original url from the DB.

2. API interface
The backend service is implemented in Django. The APIs are:
   2.1. Create QR code: A POST endpoint with the payload described above.
   2.2. Edit QR code: A PUT endpoint that allows updating the QR code name only.
        Other fields (content, format, etc.) are read-only.
   2.3. Retrieve QR code: An endpoint that will save in the DB the number
        of times the QR code was read (ie, the endpoint was called) and
        forward the user to the original url.

3. CLI interface
The CLI interface will be implemented using the typer library and have a
similar interface to the API.

4. Email confirmation
- On registration via `POST /api/signup`, a confirmation email is sent (does not auto-login)
- HTML: `/confirm-email/<token>/` validates token and redirects to success or expired page
- `/confirm-email/success/` shows confirmation success with Login button
- Expired confirmation page offers resend functionality via `POST /api/resend-confirmation`
- Tokens are single-use and time-limited by `EMAIL_CONFIRMATION_TOKEN_TTL_HOURS` (default 48)
- Login is blocked for unconfirmed users with error message

5. Forgot password
- HTML: `/forgot-password/` to request email; `/reset-password/<token>/` to set a new password
- API: `POST /api/forgot-password` (accepts `email`) and `POST /api/reset-password`
  (accepts `token`, `password`, `password_confirm`); responses avoid leaking whether the
  email exists
- Tokens are single-use and time-limited by `PASSWORD_RESET_TOKEN_TTL_HOURS` (default 4)

### Authentication
Session-based authentication using Django sessions with email confirmation.
- POST /api/signup (name, email, password) creates user and sends confirmation email (no auto-login).
- POST /api/resend-confirmation (email) resends confirmation email if account exists and unconfirmed.
- POST /api/confirm-email (token) confirms email address using valid token.
- POST /api/login (email, password) logs in and returns session id in JSON (requires confirmed email).
- POST /api/forgot-password (email) initiates password reset and returns 200 regardless of existence.
- POST /api/reset-password (token, password, password_confirm) resets password when token is valid.
- API calls require SessionAuthentication; ensure CSRF tokens are provided where applicable.
- Time-limited tokens use the `TimeLimitedToken` model with token_type field ('password_reset' or 'email_confirmation').

### QR Code Management
- GET /api/qrcodes/ - List user's QR codes (filtered by created_by, excludes soft-deleted, includes qr_type)
- POST /api/qrcodes/ - Create new QR code with full customization options (qr_type is required: 'url' or 'text')
- GET /api/qrcodes/<id>/ - Retrieve QR code details (returns 404 if soft-deleted, includes qr_type)
- PUT /api/qrcodes/<id>/ - Update QR code name only (uses QRCodeUpdateSerializer, qr_type is read-only, returns 404 if soft-deleted)
- PATCH /api/qrcodes/<id>/ - Partial update of QR code name (qr_type is read-only, returns 404 if soft-deleted)
- DELETE /api/qrcodes/<id>/ - Soft delete QR code (sets deleted_at timestamp)
- POST /api/qrcodes/preview - Generate preview without saving to DB (requires qr_type)
- QR Code Types: Each QR code has a qr_type field (QRCodeType TextChoices: URL or TEXT) that categorizes the content
- Ownership validation: Users can only access/modify their own QR codes via get_queryset filtering
- Soft delete: QR codes have a `deleted_at` field (nullable DateTimeField). When deleted:
  - `deleted_at` is set to current timestamp
  - QR code remains in database but is filtered out from all querysets
  - API endpoints return 404 for soft-deleted QR codes
  - Redirect endpoint (`/go/{short_code}/`) redirects to dashboard for soft-deleted QR codes

### HTML Pages
- `/dashboard/` - List QR codes with search (with clear button), sort, and dropdown actions per row
  - Dropdown menu includes Edit and Delete (with confirmation modal) actions
  - Delete confirmation modal displays QR code name and has Cancel/Delete buttons
- `/qrcodes/create/` - Create new QR code with qr_type selection (name 'qrcode-create')
- `/qrcodes/edit/<uuid:qr_id>/` - Edit existing QR code name; qr_type is read-only (name 'qrcode-edit')
- Both create/edit use `qrcode_editor.html` template with conditional rendering based on `qrcode` context

### Testing
Tests are located in `tests/` directory using pytest.
- test_api.py includes tests for:
  - QR code creation with various options
  - QR code listing and retrieval
  - QR code updates (name only, ownership validation, empty name validation)
  - Soft delete behavior (deleted_at field, 404 responses, list filtering)
  - Soft-deleted QR codes not appearing in list endpoint
  - Soft-deleted QR codes returning 404 on detail/update operations
  - Double-delete idempotency
  - Redirect endpoint behavior for soft-deleted QR codes
  - Authentication and authorization
  - URL shortening functionality

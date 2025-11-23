# QR Code Generator Project

## Project Overview
A Python project for generating and manipulating QR codes.

## Goals
- Create a flexible QR code generation service
- Support main QR code format
- Provide API, CLI and programmatic interfaces

## Tech Stack
- Python 3.13
- Django 5.2 for API interface
- typer for CLI interface
- segno package for QR code generation
- RDBMS for data storage

## App name and project structure
The app name is `qr_code`.
The app code should be located under `src/qr_code`.
All references should reflect this structure.
Database tables related to the app should have the prefix `qr_code`.
Models are stored under `src/qr_code/models`, each model in its own file.

## Current Status
Initial version done. Testing functionality and fixing bugs.

## Next Steps
1. Test authentication endpoints.
2. Test QRCode endpoints with session auth.
3. Fix issues as needed.

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
Frontend design language is minimal with a green-gray color palette from `src/qr_code/static/images/logo_full.png`.
All pages support light/dark mode including login and register.
Form validation includes existence checks and email format validation before backend calls.
On valid login, redirect to 'hello' page. Include a 'remember me' checkbox with corresponding behavior.
User-facing error messages are simple; developer-facing errors are verbose and technical. CSS stack uses Tailwind.

### Documentation
Create documentation in MD format under the `docs` directory, all lowercased files.
Only README.md remains in the root directory, uppercased.

### Functionality
1. Create QR code
When creating a QR code, the user should be able to specify the following:
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
   2.2. Retrieve QR code: An endpoint that will save in the DB the number
        of times the QR code was read (ie, the endpoint was called) and
        forward the user to the original url.

3. CLI interface
The CLI interface will be implemented using the typer library and have a
similar interface to the API.

### Authentication
Session-based authentication using Django sessions.
- POST /api/signup (name, email, password) creates user and logs in.
- POST /api/login (email, password) logs in and returns session id in JSON.
- API calls require SessionAuthentication; ensure CSRF tokens are provided where applicable.

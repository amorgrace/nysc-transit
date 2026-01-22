# NYSC Transit API

Lightweight Django + Django Ninja API for managing NYSC-related transit and bookings. This project implements a custom user model, vendor and corper profiles, booking flows and exposes a JSON API via Django Ninja with JWT authentication.

## Key points

- Django 6 project using Django Ninja for fast API development
- JWT authentication via `django-ninja-jwt`
- Uses `dj-database-url` and `python-decouple` for environment-driven configuration
- Static file serving with `whitenoise` and production-ready WSGI/Gunicorn/UVicorn settings

## Table of contents

- What this project contains
- Prerequisites
- Quickstart (development)
- Environment variables
- Running tests
- API routes / documentation
- Apps overview
- Deployment notes
- Contributing
- License & contact

## What this project contains

Top-level structure (important files/folders):

- `engine/` — Django project settings, URL routing and ASGI/WSGI entry points
- `apps/` — application package containing Django apps:
	- `authenticator` — custom user model and authentication routes
	- `vendor` — vendor profile and trip endpoints
	- `corper` — corper profile endpoints
	- `bookings` — booking and reservation flows
- `requirements.txt` — Python package dependencies
- `manage.py` — Django management wrapper

## Prerequisites

- macOS (instructions below use zsh)
- Python 3.10+ (the project was scaffolded for Django 6)
- PostgreSQL (recommended for production). SQLite works for quick local testing.

You can install a Python runtime using pyenv, Homebrew, or your preferred method.

## Quickstart (development)

1. Clone the repository

```bash
git clone <repo-url>
cd nysc-transit
```


2. Create and activate a virtual environment

macOS / Linux (zsh / bash)

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell / CMD / WSL)

- PowerShell (recommended):

```powershell
python -m venv .venv
# In PowerShell, use the Activate.ps1 script
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

- CMD (legacy / quick):

```cmd
python -m venv .venv
.\.venv\Scripts\activate
```

- WSL (recommended if you prefer a Linux-like environment on Windows):

Use the same commands as macOS/Linux inside your WSL distro:

```bash
python -m venv .venv
source .venv/bin/activate
```

Notes:

- On Windows PowerShell you may need to temporarily relax the execution policy to run the activation script (see the `Set-ExecutionPolicy` line above). That command only changes the policy for the current PowerShell process and does not persist.
- If you use WSL, make sure your `python` and `pip` refer to the OS distribution inside WSL.

3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. Create a `.env` file at the project root. See "Environment variables" below. Minimal working example (SQLite):

```env
SECRET_KEY=replace-me-with-a-secret
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

5. Run migrations and create a superuser

```bash
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py createsuperuser
```

6. Start the development server

```bash
python3 manage.py runserver
```

Open http://127.0.0.1:8000/ — the project root responds with a small welcome JSON.

## Environment variables

This project reads configuration from environment variables via `python-decouple` and `python-dotenv`.

- `SECRET_KEY` — Django secret key (required)
- `DEBUG` — `True` or `False` (default in code falls back to True)
- `DATABASE_URL` — A DSN string used by `dj-database-url`. Examples:
	- SQLite (local dev): `sqlite:///db.sqlite3`
	- Postgres: `postgres://USER:PASSWORD@HOST:PORT/DBNAME`

Add more variables if you adapt the settings (ALLOWED_HOSTS, email settings, SENTRY DSN, etc.).

## Running tests

Run tests using Django's test runner (this will discover TestCase-based tests):

```bash
# Run all tests (Django TestRunner)
python3 manage.py test

or

pytest

or

pytest -q

# Run tests for only a single app
python3 manage.py test modules.<appname>
```

If you add test-specific dependencies, update `requirements.txt` accordingly.

## Code formatting & linters

We use ruff (fast linter/formatter) and Black for consistent code formatting. Run these commands from the repository root.

Install (if not already installed):

```bash
pip install ruff black
```

Common commands:

```bash
# Format files with ruff's formatter
ruff format .

# Run ruff and automatically fix fixable issues
ruff check . --fix

# Run ruff in check-only mode (reports issues, doesn't modify files)
ruff check .

# Format code with Black
black .

# Check-only with Black (exit non-zero if changes would be made)
black . --check
```

Run these before commits or in CI to keep a consistent code style.


## API routes & documentation

The API root is mounted at `/api/`.

- Authentication routes: `/api/auth/` (JWT token endpoints and auth-related operations)
- Corper routes: `/api/corper/`
- Vendor routes: `/api/vendor/`
- Booking routes: `/api/bookings/`

Django Ninja exposes interactive docs by default. While the exact paths may vary, try:

- Swagger UI: `/api/docs`
- ReDoc: `/api/redoc`

These endpoints are visible in development and are a fast way to explore the API contract.

## Apps overview

- `authenticator` — Implements a custom `User` model (UUID primary key) with roles (`corper` and `vendor`). The user model lives at `apps/authenticator/models.py`. The project sets `AUTH_USER_MODEL = "authenticator.User"` in `engine/settings.py`.
- `vendor` — Vendor profiles and trip management. Use this to create vendors and manage trips associated with vendors.
- `corper` — Corper (participant) profiles and related endpoints.
- `bookings` — Booking creation, listing, and management endpoints for creating reservations against vendor trips.

Refer to each app's `views.py`, `schemas.py` (or `schema.py`) and `models.py` for request/response shapes, serializer-like schemas (pydantic/django-ninja) and business logic.

## Authentication

This project uses JWTs (via `django-ninja-jwt`) to protect API endpoints. Token lifetime and rotation are configured in `engine/settings.py` using the `SIMPLE_JWT` dict. Typical flow:

1. Authenticate with an email/password to receive access and refresh tokens
2. Send the access token in the `Authorization: Bearer <access_token>` header for protected routes
3. Use the refresh token to rotate/refresh access tokens when the access token expires

Check `apps/authenticator/views.py` for the exact endpoints and request/response details.

## Static files & assets

This project uses `whitenoise` to serve static files in production. Before deploying or running with a production server, collect static files:

```bash
python manage.py collectstatic --noinput
```

## Deployment notes

Production-ready recommendations:

- Use PostgreSQL or another production RDBMS and set `DATABASE_URL` accordingly
- Set `DEBUG=False` and configure `ALLOWED_HOSTS`
- Configure secure settings for `SECRET_KEY`, TLS, and CORS
- Use Gunicorn (WSGI) or Uvicorn/Hypercorn (ASGI) + proper process manager (systemd, supervisor) for serving
- Example Gunicorn systemd service (basic):

```ini
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/nysc-transit
ExecStart=/path/to/.venv/bin/gunicorn engine.wsgi:application -w 3 -b 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

Or run manually in a container/host:

```bash
# collect static first
python manage.py collectstatic --noinput
# run gunicorn
gunicorn engine.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

If you prefer ASGI + Uvicorn:

```bash
uvicorn engine.asgi:application --host 0.0.0.0 --port 8000
```

When deploying behind a proxy (NGINX), make sure to forward headers and serve static files efficiently.

## Contribution and development notes

- Follow repository conventions: apps live in `apps/` and use Django app config
- Tests are colocated in each app (`tests.py`) — add unit tests for new features
- Keep API schema changes backward compatible when possible

Suggested local development workflow:

1. Create a feature branch
2. Add tests for new behavior
3. Run tests and linters locally
4. Open a pull request with a concise description and testing notes

## Quality gates (developer checklist)

- [ ] All new code covered by tests where practical
- [ ] Migrations included for model changes
- [ ] Update `requirements.txt` if new packages are added

## License

This repository is currently closed-source and provided under an All Rights Reserved notice — see the `LICENSE` file in the repository root for details.

If you need access or a specific licensing arrangement for this codebase, please contact the repository owner or open an issue to request access.

## Contact / Questions

If you need help running or extending the project, open an issue or reach out to the repository owner/maintainers.

---

Happy hacking — this README is meant to get developers started quickly. If you'd like, I can add a `CONTRIBUTING.md`, a `.env.example`, or automated test runners (GitHub Actions) next.

## Updating requirements

When you add or remove Python packages while developing, update the pinned dependencies in `requirements.txt` from within your activated virtual environment:

```bash
# Activate your virtualenv first (example using the project's `.venv`):
source .venv/bin/activate

# Freeze currently installed packages to requirements.txt (overwrites file)
pip freeze > requirements.txt
```

Note: This will overwrite `requirements.txt`. If you maintain multiple requirement files (e.g., `requirements-dev.txt`), update the appropriate file instead.

## Pre-commit

To enable repository-level git hooks (recommended), run the following from the project root:

```bash
pre-commit install
pre-commit run --all-files
```

If you don't have the `pre-commit` tool installed locally, install it first:

```bash
pip install pre-commit
```

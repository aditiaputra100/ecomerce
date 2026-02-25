# GEMINI.md - E-Commerce API Context

## Project Overview
This is a modular RESTful API for an E-Commerce system built with **FastAPI**. It features a structured, maintainable architecture designed for scalability and clear separation of concerns.

### Core Technologies
- **Framework:** FastAPI
- **Language:** Python 3.13+
- **Database:** SQLite (via SQLAlchemy 2.0 ORM)
- **Package Manager:** `uv`
- **Validation:** Pydantic V2
- **Authentication:** JWT (via `python-jose` and `passlib`)
- **Testing:** Pytest

### Architecture
The project follows a modular design pattern. Each core domain (User, Products, Orders) is contained within its own directory under `app/`:
- `models.py`: SQLAlchemy database models.
- `schemas.py`: Pydantic models for request/response validation.
- `service.py`: Business logic and database operations.
- `router.py`: API endpoints and routing logic.
- `utils.py`/`dependencies.py`: Domain-specific helpers and FastAPI dependencies.

Global components:
- `app/main.py`: Application entry point and router registration.
- `app/database.py`: SQLAlchemy engine and session management.
- `app/config.py`: Environment configuration using Pydantic Settings.
- `app/exceptions.py`: Custom error types and global exception handlers.

## Building and Running

### Prerequisites
- Python 3.13+
- `uv` package manager (recommended)

### Installation
```bash
# Install dependencies
uv sync
```

### Running the Application
```bash
# Run in development mode
uv run fastapi dev app/main.py
```
The API will be available at `http://127.0.0.1:8000`. 
Interactive documentation (Swagger UI) is at `/docs`.

### Testing
```bash
# Run all tests
uv run pytest
```
Tests use an in-memory SQLite database configured in `tests/conftest.py`.

## Development Conventions

### Coding Style
- **Surgical Changes:** Keep modifications focused on the specific task.
- **Type Safety:** Use Python type hints throughout the codebase.
- **Service Layer:** Business logic should reside in `service.py` files, not in routers.
- **Error Handling:** Use custom exceptions from `app/exceptions.py` for consistent API responses.

### Database Patterns
- **Migrations:** Tables are currently created via `Base.metadata.create_all` in `main.py`. For production use, Alembic should be introduced.
- **Session Management:** Use the `get_db` dependency to inject database sessions into routers.

### Environment Configuration
- Use `.env` for sensitive settings like `SECRET_KEY`.
- Configuration is accessed via the `settings` object in `app/config.py`.

### Static Files
- Product images are stored in `app/static/uploads/products`.
- Static files are served at the `/static` prefix.

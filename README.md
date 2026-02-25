# E-Commerce API

A modular, scalable RESTful API for an E-Commerce platform built with **FastAPI**. This project features a clean architecture with clear separation of concerns, robust validation, and JWT-based authentication.

## 🚀 Features

- **Modular Architecture:** distinct domains for Users, Products, and Orders.
- **Authentication:** Secure JWT authentication with password hashing.
- **Data Validation:** Strict request/response validation using Pydantic V2.
- **Database:** SQLite with SQLAlchemy 2.0 ORM (easily swappable).
- **Testing:** Comprehensive test suite using Pytest.
- **Package Management:** Modern dependency management with `uv`.

## 🛠️ Tech Stack

- **Framework:** FastAPI
- **Language:** Python 3.13+
- **Database:** SQLite / SQLAlchemy 2.0
- **Auth:** Python-JOSE, Passlib
- **Testing:** Pytest

## 📂 Project Structure

The project follows a domain-driven structure under the `app/` directory:

```
app/
├── user/       # User management, Auth, Roles
├── products/   # Product catalog, Image handling
├── orders/     # Order processing, Cart logic
├── main.py     # Application entry point
├── config.py   # Environment configuration
└── database.py # Database connection & session
```

Each domain folder typically contains:
- `models.py`: Database tables
- `schemas.py`: API data models (Pydantic)
- `service.py`: Business logic
- `router.py`: URL endpoints

## ⚡ Getting Started

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (Recommended package manager)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd E-Commerce
    ```

2.  **Install dependencies:**
    ```bash
    uv sync
    ```

3.  **Environment Setup:**
    Create a `.env` file in the root directory (you can copy a sample if provided, or set your own):
    ```env
    SECRET_KEY=your_secret_key
    ```

### Running the Application

Start the development server:

```bash
uv run fastapi dev app/main.py
```

The API will be available at `http://127.0.0.1:8000`.

### 📖 Documentation

Interactive API documentation is automatically generated and available at:

- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`

## 🧪 Testing

Run the test suite to ensure everything is working correctly:

```bash
uv run pytest
```

# Vacancy Service

Internal company vacancy and resume management REST API.

## Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.115 |
| Validation | Pydantic v2 |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Database | PostgreSQL 16 |
| Auth | JWT (python-jose + passlib/bcrypt) |
| Server | Uvicorn |
| Tests | Pytest + pytest-asyncio + HTTPX |
| Container | Docker + docker-compose |

## Project structure

```
vacancy-service/
├── app/
│   ├── main.py              # FastAPI app, router registration
│   ├── core/
│   │   ├── config.py        # Settings (pydantic-settings)
│   │   ├── database.py      # Async engine, session, Base
│   │   ├── security.py      # JWT helpers, password hashing
│   │   └── dependencies.py  # get_current_user guard
│   ├── models/              # SQLAlchemy ORM models (3NF)
│   ├── schemas/             # Pydantic request/response schemas
│   ├── services/            # Business logic (no HTTP concerns)
│   └── routers/             # FastAPI route handlers
├── migrations/              # Alembic async migrations
│   └── versions/
│       └── 001_initial.py
├── tests/
│   ├── conftest.py          # Fixtures: client, db, auth_headers, ...
│   ├── test_auth.py
│   ├── test_categories.py
│   ├── test_positions.py
│   ├── test_vacancies.py
│   └── test_resumes.py
├── docker-compose.yml
├── docker-compose.test.yml  # Separate test PostgreSQL on port 5433
├── Dockerfile
├── requirements.txt
├── alembic.ini
├── pytest.ini
└── .env.example
```

## Data models (3NF)

| Model | Fields |
|---|---|
| **User** | id, first_name, last_name, login, hashed_password, role (admin/hr/employee) |
| **Category** | id, name |
| **Position** | id, name |
| **Vacancy** | id, title, description, position_id (FK->positions), category_id (FK->categories), status (open/closed) |
| **Resume** | id, candidate_data (JSON), category_id (FK->categories), status (active/inactive/under_review) |

## Quick start (Docker)

```bash
# 1. Copy and fill in environment variables
cp .env.example .env
# Edit SECRET_KEY at minimum

# 2. Build and start (Alembic migrations run automatically on startup)
docker-compose up --build

# API:          http://localhost:8000
# Swagger UI:   http://localhost:8000/docs
# ReDoc:        http://localhost:8000/redoc
```

## Running tests

Tests use a **separate** PostgreSQL on port 5433.

```bash
# 1. Start the test database container
docker-compose -f docker-compose.test.yml up -d

# 2. Install dependencies (Python 3.12+)
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Make sure .env has TEST_DATABASE_URL pointing to port 5433
# TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/vacancy_test_db

# 4. Run all tests with coverage report
pytest

# 5. Open HTML coverage report
start htmlcov/index.html           # Linux/Mac: open htmlcov/index.html
```

## API endpoints

All routes are prefixed with `/api/v1`.

### Auth

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | public | Register a new user |
| POST | `/auth/login` | public | Get JWT tokens (form: username/password) |
| POST | `/auth/refresh` | public | Refresh access token |
| POST | `/auth/change-password` | JWT | Change own password |

### Vacancies

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/vacancies/` | JWT | List (filters: `status`, `category_id`, `skip`, `limit`) |
| GET | `/vacancies/{id}` | JWT | Get by id |
| POST | `/vacancies/` | JWT | Create |
| PUT | `/vacancies/{id}` | JWT | Partial update |
| DELETE | `/vacancies/{id}` | JWT | Delete |

### Resumes

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/resumes/` | JWT | List (filters: `status`, `category_id`, `skip`, `limit`) |
| GET | `/resumes/{id}` | JWT | Get by id |
| POST | `/resumes/` | JWT | Create |
| PUT | `/resumes/{id}` | JWT | Partial update |
| DELETE | `/resumes/{id}` | JWT | Delete |

### Categories

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/categories/` | public | List all |
| GET | `/categories/{id}` | public | Get by id |
| POST | `/categories/` | JWT | Create |
| PUT | `/categories/{id}` | JWT | Update |
| DELETE | `/categories/{id}` | JWT | Delete |

### Positions

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/positions/` | public | List all |
| GET | `/positions/{id}` | public | Get by id |
| POST | `/positions/` | JWT | Create |
| PUT | `/positions/{id}` | JWT | Update |
| DELETE | `/positions/{id}` | JWT | Delete |

## HTTP error codes

| Code | When |
|---|---|
| 400 | Business rule violation (duplicate login, wrong old password, …) |
| 401 | Missing / invalid / expired JWT |
| 404 | Resource not found |
| 422 | Pydantic validation error (wrong field type, constraint violated) |

## Environment variables

See [.env.example](.env.example). Key variables:

| Variable | Description |
|---|---|
| `DATABASE_URL` | asyncpg connection URL for the app |
| `TEST_DATABASE_URL` | asyncpg connection URL for pytest |
| `SECRET_KEY` | Random string >= 32 chars for JWT signing |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Default: 30 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Default: 7 |

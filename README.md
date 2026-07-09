# Cinema App

FastAPI-based cinema management REST API with async SQLAlchemy and SQLite (dev) / PostgreSQL (prod).

## Database Schema

![DB Schema](docs/db_schema.png)

## Quick Start

```bash
pip install -r requirements.txt

# Apply database migrations (creates all tables)
alembic upgrade head

# Start the server
uvicorn main:app --reload
```

## Migrations

Tables are managed via **Alembic** — never created automatically on startup.

```bash
# Apply all pending migrations
alembic upgrade head

# Create a new migration after changing models
alembic revision --autogenerate -m "describe the change"

# Rollback one step
alembic downgrade -1

# Show current migration state
alembic current
```

Set `DATABASE_URL` env variable to use PostgreSQL:

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host/db alembic upgrade head
```

Swagger UI: `http://127.0.0.1:8000/docs`

---

## API Endpoints

### Genres `/api/v1/genres`

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/v1/genres/` | Get all genres |
| GET | `/api/v1/genres/{genre_id}` | Get genre by ID |
| POST | `/api/v1/genres/` | Create genre |
| PUT | `/api/v1/genres/{genre_id}` | Update genre |
| DELETE | `/api/v1/genres/{genre_id}` | Delete genre |

### Actors `/api/v1/actors`

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/v1/actors/` | Get all actors |
| GET | `/api/v1/actors/{actor_id}` | Get actor by ID |
| POST | `/api/v1/actors/` | Create actor |
| PUT | `/api/v1/actors/{actor_id}` | Update actor |
| DELETE | `/api/v1/actors/{actor_id}` | Delete actor |

### Movies `/api/v1/movies`

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/v1/movies/` | Get all movies (with actors & genres) |
| GET | `/api/v1/movies/{movie_id}` | Get movie by ID |
| POST | `/api/v1/movies/` | Create movie |
| PUT | `/api/v1/movies/{movie_id}` | Update movie |
| DELETE | `/api/v1/movies/{movie_id}` | Delete movie |

### Users `/api/v1/users`

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/v1/users/` | Get all users |
| GET | `/api/v1/users/{user_id}` | Get user by ID |
| POST | `/api/v1/users/` | Create user (password is hashed) |
| PUT | `/api/v1/users/{user_id}` | Update user |
| DELETE | `/api/v1/users/{user_id}` | Delete user |

### Halls `/api/v1/halls`

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/v1/halls/` | Get all halls (with seats) |
| GET | `/api/v1/halls/{hall_id}` | Get hall by ID |
| POST | `/api/v1/halls/` | Create hall |
| PUT | `/api/v1/halls/{hall_id}` | Update hall |
| DELETE | `/api/v1/halls/{hall_id}` | Delete hall |

### Sessions `/api/v1/sessions`

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/v1/sessions/` | Get all sessions (with movie & hall) |
| GET | `/api/v1/sessions/{session_id}` | Get session by ID |
| GET | `/api/v1/sessions/movie/{movie_id}` | Get sessions by movie |
| GET | `/api/v1/sessions/hall/{hall_id}` | Get sessions by hall |
| POST | `/api/v1/sessions/` | Create session |
| PUT | `/api/v1/sessions/{session_id}` | Update session |
| DELETE | `/api/v1/sessions/{session_id}` | Delete session |

### Bookings `/api/v1/bookings`

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/v1/bookings/{booking_id}` | Get booking by ID |
| GET | `/api/v1/bookings/user/{user_id}` | Get all bookings for a user |
| GET | `/api/v1/bookings/session/{session_id}` | Get all bookings for a session |
| POST | `/api/v1/bookings/` | Create booking |
| PUT | `/api/v1/bookings/{booking_id}` | Update booking status |
| DELETE | `/api/v1/bookings/{booking_id}` | Delete booking |

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 204 | Deleted (no content) |
| 404 | Not found |
| 409 | Conflict (duplicate) |
| 500 | Internal server error |

---

## Seed Data

Run seed script to populate the database with test data:

```bash
python seed.py
```

---

## Tests

Tests use **pytest** with **pytest-asyncio** and an in-memory SQLite database — no external dependencies required.

### Stack

| Tool | Purpose |
|------|---------|
| `pytest` + `pytest-asyncio` | Async test runner |
| `httpx` + `ASGITransport` | HTTP client against the FastAPI app |
| `SQLite` (in-memory, `StaticPool`) | Isolated test database |
| `pytest.mark.parametrize` | Data-driven test cases |
| `unittest.mock.patch` | Simulate DB errors in error-path tests |
| `pytest-cov` | Coverage reporting |

### Running tests

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=app --cov-report=term-missing
```

### Coverage

Minimum required coverage to commit: **85%**. The CI check will fail if coverage drops below this threshold.

Run with the fail-under flag to enforce it locally:

```bash
pytest --cov=app --cov-fail-under=85
```

### Test files

| File | What it covers |
|------|---------------|
| `tests/test_genres.py` | CRUD + pagination + not-found + duplicate |
| `tests/test_actors.py` | CRUD + pagination + field updates |
| `tests/test_movies.py` | CRUD + M2M actor/genre assignment |
| `tests/test_users.py` | CRUD + password hashing + duplicate username/email |
| `tests/test_halls.py` | CRUD + hall type variants |
| `tests/test_seats.py` | CRUD-level seat operations (no HTTP endpoint) |
| `tests/test_sessions.py` | CRUD + filter by movie/hall + status transitions |
| `tests/test_bookings.py` | CRUD + confirmed sets `paid_at` + multi-seat booking |
| `tests/test_error_paths.py` | 500 responses, `SQLAlchemyError` in read/write CRUD, `NotFoundError`, `AlreadyExistsError` |

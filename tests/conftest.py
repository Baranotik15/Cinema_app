import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
import app.models
from app.database import Base, get_db
from main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db(db_engine):
    factory = async_sessionmaker(
        bind=db_engine, class_=AsyncSession,
        autocommit=False, autoflush=False, expire_on_commit=False,
    )
    async with factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_engine):
    factory = async_sessionmaker(
        bind=db_engine, class_=AsyncSession,
        autocommit=False, autoflush=False, expire_on_commit=False,
    )

    async def override_get_db():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ---------- reusable entity fixtures ----------

@pytest_asyncio.fixture
async def genre(client):
    resp = await client.post("/api/v1/genres/", json={"name": "Action"})
    assert resp.status_code == 201
    return resp.json()


@pytest_asyncio.fixture
async def actor(client):
    resp = await client.post("/api/v1/actors/", json={
        "name": "Tom Hanks", "bio": "Legendary actor",
        "age": 65, "gender": "male",
        "image_url": "https://placehold.co/200x200/png",
    })
    assert resp.status_code == 201
    return resp.json()


@pytest_asyncio.fixture
async def movie(client, genre, actor):
    resp = await client.post("/api/v1/movies/", json={
        "title": "Test Movie",
        "description": "A test movie",
        "duration": 120,
        "year": 2024,
        "rating": 8.0,
        "poster_url": "https://placehold.co/300x450/png",
        "actor_ids": [actor["id"]],
        "genre_ids": [genre["id"]],
    })
    assert resp.status_code == 201
    return resp.json()


@pytest_asyncio.fixture
async def hall(client):
    resp = await client.post("/api/v1/halls/", json={
        "name": "Main Hall", "capacity": 100, "hall_type": "2D",
    })
    assert resp.status_code == 201
    return resp.json()


@pytest_asyncio.fixture
async def seat(db, hall):
    from app.crud.seat import create_seat
    from app.schemas.seat import SeatCreate
    s = await create_seat(db, SeatCreate(hall_id=hall["id"], row=1, number=1))
    return {"id": s.id, "hall_id": s.hall_id, "row": s.row, "number": s.number}


@pytest_asyncio.fixture
async def user(client):
    resp = await client.post("/api/v1/users/", json={
        "username": "testuser", "email": "test@example.com", "password": "password123",
    })
    assert resp.status_code == 201
    return resp.json()


@pytest_asyncio.fixture
async def session_obj(client, movie, hall):
    resp = await client.post("/api/v1/sessions/", json={
        "movie_id": movie["id"],
        "hall_id": hall["id"],
        "start_time": "2026-06-15T14:00:00",
        "price": 12.5,
        "status": "scheduled",
    })
    assert resp.status_code == 201
    return resp.json()


@pytest_asyncio.fixture
async def booking(client, user, session_obj, seat):
    resp = await client.post("/api/v1/bookings/", json={
        "user_id": user["id"],
        "session_id": session_obj["id"],
        "seat_id": seat["id"],
    })
    assert resp.status_code == 201
    return resp.json()

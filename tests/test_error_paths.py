"""
Tests for exception handling paths in CRUD and API layers.
Mocks are used to trigger SQLAlchemyError and DatabaseError code branches.
"""
import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.exceptions import DatabaseError, NotFoundError, AlreadyExistsError
from app.schemas.genre import GenreCreate, GenreUpdate
from app.schemas.actor import ActorCreate, ActorUpdate
from app.schemas.movie import MovieCreate, MovieUpdate
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.hall import HallCreate, HallUpdate
from app.schemas.seat import SeatCreate, SeatUpdate
from app.schemas.session import SessionCreate, SessionUpdate
from app.schemas.booking import BookingCreate, BookingUpdate


# ============================================================
# API — 500 error paths (DatabaseError → HTTPException 500)
# ============================================================

@pytest.mark.parametrize("url,target", [
    ("/api/v1/genres/",   "app.crud.genre.get_genres"),
    ("/api/v1/actors/",   "app.crud.actor.get_actors"),
    ("/api/v1/movies/",   "app.crud.movie.get_movies"),
    ("/api/v1/users/",    "app.crud.user.get_users"),
    ("/api/v1/halls/",    "app.crud.hall.get_halls"),
    ("/api/v1/sessions/", "app.crud.session.get_sessions"),
])
async def test_list_endpoint_returns_500_on_db_error(client, url, target):
    with patch(target, new_callable=AsyncMock, side_effect=DatabaseError("db down")):
        resp = await client.get(url)
        assert resp.status_code == 500


@pytest.mark.parametrize("url,target", [
    ("/api/v1/genres/1",   "app.crud.genre.get_genre"),
    ("/api/v1/actors/1",   "app.crud.actor.get_actor"),
    ("/api/v1/movies/1",   "app.crud.movie.get_movie"),
    ("/api/v1/users/1",    "app.crud.user.get_user"),
    ("/api/v1/halls/1",    "app.crud.hall.get_hall"),
    ("/api/v1/sessions/1", "app.crud.session.get_session"),
    ("/api/v1/bookings/1", "app.crud.booking.get_booking"),
])
async def test_get_by_id_returns_500_on_db_error(client, url, target):
    with patch(target, new_callable=AsyncMock, side_effect=DatabaseError("db down")):
        resp = await client.get(url)
        assert resp.status_code == 500


@pytest.mark.parametrize("url,target,body", [
    ("/api/v1/genres/",   "app.crud.genre.create_genre",   {"name": "X"}),
    ("/api/v1/actors/",   "app.crud.actor.create_actor",   {"name": "X"}),
    ("/api/v1/movies/",   "app.crud.movie.create_movie",   {"title": "X"}),
    ("/api/v1/users/",    "app.crud.user.create_user",     {"username": "u", "email": "u@e.com", "password": "p"}),
    ("/api/v1/halls/",    "app.crud.hall.create_hall",     {"name": "H", "capacity": 50, "hall_type": "2D"}),
])
async def test_create_endpoint_returns_500_on_db_error(client, url, target, body):
    with patch(target, new_callable=AsyncMock, side_effect=DatabaseError("db down")):
        resp = await client.post(url, json=body)
        assert resp.status_code == 500


async def test_create_session_returns_500_on_db_error(client, movie, hall):
    with patch("app.crud.session.create_session", new_callable=AsyncMock, side_effect=DatabaseError("db down")):
        resp = await client.post("/api/v1/sessions/", json={
            "movie_id": movie["id"], "hall_id": hall["id"],
            "start_time": "2026-06-15T14:00:00", "price": 10.0, "status": "scheduled",
        })
        assert resp.status_code == 500


async def test_create_booking_returns_500_on_db_error(client, user, session_obj, seat):
    with patch("app.crud.booking.create_booking", new_callable=AsyncMock, side_effect=DatabaseError("db down")):
        resp = await client.post("/api/v1/bookings/", json={
            "user_id": user["id"], "session_id": session_obj["id"], "seat_id": seat["id"],
        })
        assert resp.status_code == 500


@pytest.mark.parametrize("url,target,body", [
    ("/api/v1/genres/1",   "app.crud.genre.update_genre",   {"name": "x"}),
    ("/api/v1/actors/1",   "app.crud.actor.update_actor",   {"name": "x"}),
    ("/api/v1/movies/1",   "app.crud.movie.update_movie",   {"title": "x"}),
    ("/api/v1/users/1",    "app.crud.user.update_user",     {"username": "x"}),
    ("/api/v1/halls/1",    "app.crud.hall.update_hall",     {"name": "x"}),
    ("/api/v1/sessions/1", "app.crud.session.update_session", {"price": 10.0}),
    ("/api/v1/bookings/1", "app.crud.booking.update_booking", {"status": "confirmed"}),
])
async def test_update_endpoint_returns_500_on_db_error(client, url, target, body):
    with patch(target, new_callable=AsyncMock, side_effect=DatabaseError("db down")):
        resp = await client.put(url, json=body)
        assert resp.status_code == 500


@pytest.mark.parametrize("url,target", [
    ("/api/v1/genres/1",   "app.crud.genre.delete_genre"),
    ("/api/v1/actors/1",   "app.crud.actor.delete_actor"),
    ("/api/v1/movies/1",   "app.crud.movie.delete_movie"),
    ("/api/v1/users/1",    "app.crud.user.delete_user"),
    ("/api/v1/halls/1",    "app.crud.hall.delete_hall"),
    ("/api/v1/sessions/1", "app.crud.session.delete_session"),
    ("/api/v1/bookings/1", "app.crud.booking.delete_booking"),
])
async def test_delete_endpoint_returns_500_on_db_error(client, url, target):
    with patch(target, new_callable=AsyncMock, side_effect=DatabaseError("db down")):
        resp = await client.delete(url)
        assert resp.status_code == 500


async def test_sessions_by_movie_returns_500_on_db_error(client):
    with patch("app.crud.session.get_sessions_by_movie", new_callable=AsyncMock, side_effect=DatabaseError("db down")):
        resp = await client.get("/api/v1/sessions/movie/1")
        assert resp.status_code == 500


async def test_sessions_by_hall_returns_500_on_db_error(client):
    with patch("app.crud.session.get_sessions_by_hall", new_callable=AsyncMock, side_effect=DatabaseError("db down")):
        resp = await client.get("/api/v1/sessions/hall/1")
        assert resp.status_code == 500


async def test_bookings_by_user_returns_500_on_db_error(client):
    with patch("app.crud.booking.get_bookings_by_user", new_callable=AsyncMock, side_effect=DatabaseError("db down")):
        resp = await client.get("/api/v1/bookings/user/1")
        assert resp.status_code == 500


async def test_bookings_by_session_returns_500_on_db_error(client):
    with patch("app.crud.booking.get_bookings_by_session", new_callable=AsyncMock, side_effect=DatabaseError("db down")):
        resp = await client.get("/api/v1/bookings/session/1")
        assert resp.status_code == 500


# ============================================================
# CRUD — SQLAlchemyError in read functions (mock db.execute)
# ============================================================

async def test_genre_get_sql_error(db):
    from app.crud.genre import get_genre, get_genres
    with patch.object(db, "execute", new_callable=AsyncMock, side_effect=SQLAlchemyError("err")):
        with pytest.raises(DatabaseError):
            await get_genres(db)
    with patch.object(db, "execute", new_callable=AsyncMock, side_effect=SQLAlchemyError("err")):
        with pytest.raises(DatabaseError):
            await get_genre(db, 1)


async def test_actor_get_sql_error(db):
    from app.crud.actor import get_actor, get_actors
    with patch.object(db, "execute", new_callable=AsyncMock, side_effect=SQLAlchemyError("err")):
        with pytest.raises(DatabaseError):
            await get_actors(db)
    with patch.object(db, "execute", new_callable=AsyncMock, side_effect=SQLAlchemyError("err")):
        with pytest.raises(DatabaseError):
            await get_actor(db, 1)


async def test_movie_get_sql_error(db):
    from app.crud.movie import get_movie, get_movies
    with patch.object(db, "execute", new_callable=AsyncMock, side_effect=SQLAlchemyError("err")):
        with pytest.raises(DatabaseError):
            await get_movies(db)
    with patch.object(db, "execute", new_callable=AsyncMock, side_effect=SQLAlchemyError("err")):
        with pytest.raises(DatabaseError):
            await get_movie(db, 1)


async def test_user_get_sql_error(db):
    from app.crud.user import get_user, get_users, get_user_by_email
    with patch.object(db, "execute", new_callable=AsyncMock, side_effect=SQLAlchemyError("err")):
        with pytest.raises(DatabaseError):
            await get_users(db)
    with patch.object(db, "execute", new_callable=AsyncMock, side_effect=SQLAlchemyError("err")):
        with pytest.raises(DatabaseError):
            await get_user(db, 1)
    with patch.object(db, "execute", new_callable=AsyncMock, side_effect=SQLAlchemyError("err")):
        with pytest.raises(DatabaseError):
            await get_user_by_email(db, "test@example.com")


async def test_hall_get_sql_error(db):
    from app.crud.hall import get_hall, get_halls
    with patch.object(db, "execute", new_callable=AsyncMock, side_effect=SQLAlchemyError("err")):
        with pytest.raises(DatabaseError):
            await get_halls(db)
    with patch.object(db, "execute", new_callable=AsyncMock, side_effect=SQLAlchemyError("err")):
        with pytest.raises(DatabaseError):
            await get_hall(db, 1)


async def test_seat_get_sql_error(db):
    from app.crud.seat import get_seat, get_seats_by_hall
    with patch.object(db, "execute", new_callable=AsyncMock, side_effect=SQLAlchemyError("err")):
        with pytest.raises(DatabaseError):
            await get_seat(db, 1)
    with patch.object(db, "execute", new_callable=AsyncMock, side_effect=SQLAlchemyError("err")):
        with pytest.raises(DatabaseError):
            await get_seats_by_hall(db, 1)


async def test_session_get_sql_error(db):
    from app.crud.session import get_session, get_sessions, get_sessions_by_movie, get_sessions_by_hall
    with patch.object(db, "execute", new_callable=AsyncMock, side_effect=SQLAlchemyError("err")):
        with pytest.raises(DatabaseError):
            await get_sessions(db)
    with patch.object(db, "execute", new_callable=AsyncMock, side_effect=SQLAlchemyError("err")):
        with pytest.raises(DatabaseError):
            await get_session(db, 1)
    with patch.object(db, "execute", new_callable=AsyncMock, side_effect=SQLAlchemyError("err")):
        with pytest.raises(DatabaseError):
            await get_sessions_by_movie(db, 1)
    with patch.object(db, "execute", new_callable=AsyncMock, side_effect=SQLAlchemyError("err")):
        with pytest.raises(DatabaseError):
            await get_sessions_by_hall(db, 1)


async def test_booking_get_sql_error(db):
    from app.crud.booking import get_booking, get_bookings_by_user, get_bookings_by_session
    with patch.object(db, "execute", new_callable=AsyncMock, side_effect=SQLAlchemyError("err")):
        with pytest.raises(DatabaseError):
            await get_booking(db, 1)
    with patch.object(db, "execute", new_callable=AsyncMock, side_effect=SQLAlchemyError("err")):
        with pytest.raises(DatabaseError):
            await get_bookings_by_user(db, 1)
    with patch.object(db, "execute", new_callable=AsyncMock, side_effect=SQLAlchemyError("err")):
        with pytest.raises(DatabaseError):
            await get_bookings_by_session(db, 1)


# ============================================================
# CRUD — SQLAlchemyError in write functions
# Each operation gets its own session to avoid state carryover.
# We use a plain async function (not AsyncMock) to avoid
# AsyncMock's coroutine cancellation conflicting with SQLAlchemy greenlets.
# ============================================================

async def _commit_err(*a, **kw):
    raise SQLAlchemyError("forced db error")


async def test_genre_write_sql_error(db_engine):
    from app.crud.genre import create_genre, update_genre, delete_genre
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
    mk = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)

    async with mk() as s:
        with patch.object(s, "commit", new=_commit_err):
            with pytest.raises(DatabaseError):
                await create_genre(s, GenreCreate(name="ErrGenre"))

    async with mk() as s:
        g = await create_genre(s, GenreCreate(name="TempGenre"))

    async with mk() as s:
        with patch.object(s, "commit", new=_commit_err):
            with pytest.raises(DatabaseError):
                await update_genre(s, g.id, GenreUpdate(name="Y"))

    async with mk() as s:
        with patch.object(s, "commit", new=_commit_err):
            with pytest.raises(DatabaseError):
                await delete_genre(s, g.id)


async def test_actor_write_sql_error(db_engine):
    from app.crud.actor import create_actor, update_actor, delete_actor
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
    mk = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)

    async with mk() as s:
        with patch.object(s, "commit", new=_commit_err):
            with pytest.raises(DatabaseError):
                await create_actor(s, ActorCreate(name="ErrActor"))

    async with mk() as s:
        a = await create_actor(s, ActorCreate(name="TempActor"))

    async with mk() as s:
        with patch.object(s, "commit", new=_commit_err):
            with pytest.raises(DatabaseError):
                await update_actor(s, a.id, ActorUpdate(name="Y"))

    async with mk() as s:
        with patch.object(s, "commit", new=_commit_err):
            with pytest.raises(DatabaseError):
                await delete_actor(s, a.id)


async def test_user_write_sql_error(db_engine):
    from app.crud.user import create_user, update_user, delete_user
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
    mk = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)

    async with mk() as s:
        with patch.object(s, "commit", new=_commit_err):
            with pytest.raises(DatabaseError):
                await create_user(s, UserCreate(username="erruser", email="err@e.com", password="p"), "h")

    async with mk() as s:
        u = await create_user(s, UserCreate(username="tmpuser", email="tmp@e.com", password="p"), "h")

    async with mk() as s:
        with patch.object(s, "commit", new=_commit_err):
            with pytest.raises(DatabaseError):
                await update_user(s, u.id, UserUpdate(username="newname"))

    async with mk() as s:
        with patch.object(s, "commit", new=_commit_err):
            with pytest.raises(DatabaseError):
                await delete_user(s, u.id)


async def test_hall_write_sql_error(db_engine):
    from app.crud.hall import create_hall, update_hall, delete_hall
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
    mk = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)

    async with mk() as s:
        with patch.object(s, "commit", new=_commit_err):
            with pytest.raises(DatabaseError):
                await create_hall(s, HallCreate(name="ErrHall", capacity=50, hall_type="2D"))

    async with mk() as s:
        h = await create_hall(s, HallCreate(name="TempHall", capacity=50, hall_type="2D"))

    async with mk() as s:
        with patch.object(s, "commit", new=_commit_err):
            with pytest.raises(DatabaseError):
                await update_hall(s, h.id, HallUpdate(name="Updated"))

    async with mk() as s:
        with patch.object(s, "commit", new=_commit_err):
            with pytest.raises(DatabaseError):
                await delete_hall(s, h.id)


async def test_seat_write_sql_error(db_engine, hall):
    from app.crud.seat import create_seat, update_seat, delete_seat, create_seats_bulk
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
    mk = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)

    async with mk() as s:
        with patch.object(s, "commit", new=_commit_err):
            with pytest.raises(DatabaseError):
                await create_seat(s, SeatCreate(hall_id=hall["id"], row=1, number=1))

    async with mk() as s:
        with patch.object(s, "commit", new=_commit_err):
            with pytest.raises(DatabaseError):
                await create_seats_bulk(s, [SeatCreate(hall_id=hall["id"], row=1, number=1)])

    async with mk() as s:
        seat_obj = await create_seat(s, SeatCreate(hall_id=hall["id"], row=2, number=2))

    async with mk() as s:
        with patch.object(s, "commit", new=_commit_err):
            with pytest.raises(DatabaseError):
                await update_seat(s, seat_obj.id, SeatUpdate(row=9))

    async with mk() as s:
        with patch.object(s, "commit", new=_commit_err):
            with pytest.raises(DatabaseError):
                await delete_seat(s, seat_obj.id)


async def test_booking_write_sql_error(db_engine, user, session_obj, seat):
    from app.crud.booking import create_booking, update_booking, delete_booking
    from app.crud.seat import create_seat
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
    mk = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)

    async with mk() as s:
        with patch.object(s, "commit", new=_commit_err):
            with pytest.raises(DatabaseError):
                await create_booking(s, BookingCreate(
                    user_id=user["id"], session_id=session_obj["id"], seat_id=seat["id"],
                ))

    async with mk() as s:
        s2 = await create_seat(s, SeatCreate(hall_id=seat["hall_id"], row=9, number=9))
    async with mk() as s:
        b = await create_booking(s, BookingCreate(
            user_id=user["id"], session_id=session_obj["id"], seat_id=s2.id,
        ))

    async with mk() as s:
        with patch.object(s, "commit", new=_commit_err):
            with pytest.raises(DatabaseError):
                await update_booking(s, b.id, BookingUpdate(status="confirmed"))

    async with mk() as s:
        with patch.object(s, "commit", new=_commit_err):
            with pytest.raises(DatabaseError):
                await delete_booking(s, b.id)


# ============================================================
# CRUD — NotFoundError on update/delete of non-existent entity
# ============================================================

async def test_crud_not_found_errors(db):
    from app.crud.genre import update_genre, delete_genre
    from app.crud.actor import update_actor, delete_actor
    from app.crud.user import update_user, delete_user
    from app.crud.hall import update_hall, delete_hall
    from app.crud.seat import update_seat, delete_seat
    from app.crud.session import update_session, delete_session
    from app.crud.booking import update_booking, delete_booking

    for fn, arg in [
        (lambda: update_genre(db, 9999, GenreUpdate(name="x")), None),
        (lambda: delete_genre(db, 9999), None),
        (lambda: update_actor(db, 9999, ActorUpdate(name="x")), None),
        (lambda: delete_actor(db, 9999), None),
        (lambda: update_user(db, 9999, UserUpdate(username="x")), None),
        (lambda: delete_user(db, 9999), None),
        (lambda: update_hall(db, 9999, HallUpdate(name="x")), None),
        (lambda: delete_hall(db, 9999), None),
        (lambda: update_seat(db, 9999, SeatUpdate(row=1)), None),
        (lambda: delete_seat(db, 9999), None),
        (lambda: update_session(db, 9999, SessionUpdate(price=1.0)), None),
        (lambda: delete_session(db, 9999), None),
        (lambda: update_booking(db, 9999, BookingUpdate(status="confirmed")), None),
        (lambda: delete_booking(db, 9999), None),
    ]:
        with pytest.raises(NotFoundError):
            await fn()


# ============================================================
# CRUD — AlreadyExistsError (duplicate)
# ============================================================

async def test_crud_already_exists_errors(db):
    from app.crud.genre import create_genre, update_genre
    from app.crud.actor import create_actor
    from app.crud.hall import create_hall
    from app.crud.user import create_user

    await create_genre(db, GenreCreate(name="UniqueGenre"))
    with pytest.raises(AlreadyExistsError):
        await create_genre(db, GenreCreate(name="UniqueGenre"))

    g2 = await create_genre(db, GenreCreate(name="G2"))
    await create_genre(db, GenreCreate(name="G3"))
    with pytest.raises(AlreadyExistsError):
        await update_genre(db, g2.id, GenreUpdate(name="G3"))

    await create_hall(db, HallCreate(name="UniqueHall", capacity=50, hall_type="2D"))
    with pytest.raises(AlreadyExistsError):
        await create_hall(db, HallCreate(name="UniqueHall", capacity=100, hall_type="3D"))

    await create_user(db, UserCreate(username="u1", email="u1@e.com", password="p"), "h")
    with pytest.raises(AlreadyExistsError):
        await create_user(db, UserCreate(username="u1", email="other@e.com", password="p"), "h")


# ============================================================
# CRUD — get_user_by_email (not exercised by API tests)
# ============================================================

async def test_get_user_by_email(db):
    from app.crud.user import create_user, get_user_by_email

    u = await create_user(db, UserCreate(username="emailtest", email="findme@e.com", password="p"), "hashed")
    found = await get_user_by_email(db, "findme@e.com")
    assert found is not None
    assert found.id == u.id

    not_found = await get_user_by_email(db, "nobody@e.com")
    assert not_found is None


# ============================================================
# CRUD — session write sql error
# ============================================================

async def test_session_write_sql_error(db_engine, movie, hall):
    from app.crud.session import create_session, update_session, delete_session
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
    mk = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)

    async with mk() as s:
        with patch.object(s, "commit", new=_commit_err):
            with pytest.raises(DatabaseError):
                await create_session(s, SessionCreate(
                    movie_id=movie["id"], hall_id=hall["id"],
                    start_time="2026-06-15T14:00:00", price=10.0, status="scheduled",
                ))

    async with mk() as s:
        sess_obj = await create_session(s, SessionCreate(
            movie_id=movie["id"], hall_id=hall["id"],
            start_time="2026-06-20T10:00:00", price=15.0, status="scheduled",
        ))

    async with mk() as s:
        with patch.object(s, "commit", new=_commit_err):
            with pytest.raises(DatabaseError):
                await update_session(s, sess_obj.id, SessionUpdate(price=99.0))

    async with mk() as s:
        with patch.object(s, "commit", new=_commit_err):
            with pytest.raises(DatabaseError):
                await delete_session(s, sess_obj.id)


# ============================================================
# CRUD — movie write sql error
# ============================================================

async def test_movie_write_sql_error(db_engine):
    from app.crud.movie import create_movie, update_movie, delete_movie
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
    mk = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)

    async with mk() as s:
        with patch.object(s, "commit", new=_commit_err):
            with pytest.raises(DatabaseError):
                await create_movie(s, MovieCreate(title="ErrMovie"))

    async with mk() as s:
        m = await create_movie(s, MovieCreate(title="TempMovie"))

    async with mk() as s:
        with patch.object(s, "commit", new=_commit_err):
            with pytest.raises(DatabaseError):
                await update_movie(s, m.id, MovieUpdate(title="Updated"))

    async with mk() as s:
        with patch.object(s, "commit", new=_commit_err):
            with pytest.raises(DatabaseError):
                await delete_movie(s, m.id)

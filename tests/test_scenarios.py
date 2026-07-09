"""
Scenario (integration) tests — verify business flows across multiple endpoints.
Each test exercises a real chain of API calls without mocks.
"""
import pytest

GENRES   = "/api/v1/genres/"
ACTORS   = "/api/v1/actors/"
MOVIES   = "/api/v1/movies/"
HALLS    = "/api/v1/halls/"
SESSIONS = "/api/v1/sessions/"
USERS    = "/api/v1/users/"
BOOKINGS = "/api/v1/bookings/"


# ------------------------------------------------------------------ helpers --

async def _create_seat(db, hall_id, row, number):
    from app.crud.seat import create_seat
    from app.schemas.seat import SeatCreate
    s = await create_seat(db, SeatCreate(hall_id=hall_id, row=row, number=number))
    return s.id


# ============================================================
# Scenario 1: Full chain — movie → session → booking → confirm
# ============================================================

async def test_full_booking_lifecycle(client, db):
    """Create the full object graph and walk a booking from pending to confirmed."""
    genre  = (await client.post(GENRES,  json={"name": "Drama"})).json()
    actor  = (await client.post(ACTORS,  json={"name": "Meryl Streep", "age": 74, "gender": "female"})).json()
    movie  = (await client.post(MOVIES,  json={
        "title": "The Post", "duration": 116, "year": 2017,
        "actor_ids": [actor["id"]], "genre_ids": [genre["id"]],
    })).json()
    hall   = (await client.post(HALLS,   json={"name": "Hall A", "capacity": 50, "hall_type": "2D"})).json()
    session = (await client.post(SESSIONS, json={
        "movie_id": movie["id"], "hall_id": hall["id"],
        "start_time": "2026-07-01T18:00:00", "price": 15.0, "status": "scheduled",
    })).json()
    user   = (await client.post(USERS,   json={"username": "alice", "email": "alice@e.com", "password": "pw"})).json()
    seat_id = await _create_seat(db, hall["id"], row=1, number=1)

    # Create booking — default status is pending
    resp = await client.post(BOOKINGS, json={
        "user_id": user["id"], "session_id": session["id"], "seat_id": seat_id,
    })
    assert resp.status_code == 201
    booking = resp.json()
    assert booking["status"] == "pending"
    assert booking["paid_at"] is None

    # Confirm booking — paid_at must be set
    resp = await client.put(f"{BOOKINGS}{booking['id']}", json={"status": "confirmed"})
    assert resp.status_code == 200
    confirmed = resp.json()
    assert confirmed["status"] == "confirmed"
    assert confirmed["paid_at"] is not None

    # Verify nested response contains correct movie title
    assert confirmed["session"]["movie"]["title"] == "The Post"
    assert confirmed["session"]["hall"]["id"] == hall["id"]


# ============================================================
# Scenario 2: Two users book different seats in the same session
# ============================================================

async def test_two_users_book_same_session(client, db, movie, hall, session_obj):
    user1 = (await client.post(USERS, json={"username": "bob",   "email": "bob@e.com",   "password": "pw"})).json()
    user2 = (await client.post(USERS, json={"username": "carol", "email": "carol@e.com", "password": "pw"})).json()

    seat1 = await _create_seat(db, hall["id"], row=2, number=1)
    seat2 = await _create_seat(db, hall["id"], row=2, number=2)

    r1 = await client.post(BOOKINGS, json={"user_id": user1["id"], "session_id": session_obj["id"], "seat_id": seat1})
    r2 = await client.post(BOOKINGS, json={"user_id": user2["id"], "session_id": session_obj["id"], "seat_id": seat2})
    assert r1.status_code == 201
    assert r2.status_code == 201

    # Session should now have 2 bookings
    resp = await client.get(f"{BOOKINGS}session/{session_obj['id']}")
    assert resp.status_code == 200
    assert len(resp.json()) == 2
    user_ids = {b["user_id"] for b in resp.json()}
    assert user1["id"] in user_ids
    assert user2["id"] in user_ids


# ============================================================
# Scenario 3: One user books across two different sessions
# ============================================================

async def test_user_books_multiple_sessions(client, db, user, movie, hall):
    session1 = (await client.post(SESSIONS, json={
        "movie_id": movie["id"], "hall_id": hall["id"],
        "start_time": "2026-07-10T10:00:00", "price": 10.0, "status": "scheduled",
    })).json()
    session2 = (await client.post(SESSIONS, json={
        "movie_id": movie["id"], "hall_id": hall["id"],
        "start_time": "2026-07-11T10:00:00", "price": 10.0, "status": "scheduled",
    })).json()

    seat1 = await _create_seat(db, hall["id"], row=3, number=1)
    seat2 = await _create_seat(db, hall["id"], row=3, number=2)

    await client.post(BOOKINGS, json={"user_id": user["id"], "session_id": session1["id"], "seat_id": seat1})
    await client.post(BOOKINGS, json={"user_id": user["id"], "session_id": session2["id"], "seat_id": seat2})

    resp = await client.get(f"{BOOKINGS}user/{user['id']}")
    assert resp.status_code == 200
    bookings = resp.json()
    assert len(bookings) == 2
    session_ids = {b["session_id"] for b in bookings}
    assert session1["id"] in session_ids
    assert session2["id"] in session_ids


# ============================================================
# Scenario 4: Booking status transitions
# ============================================================

@pytest.mark.parametrize("transitions", [
    ["confirmed"],
    ["cancelled"],
    ["confirmed", "cancelled"],
    ["cancelled", "confirmed"],
])
async def test_booking_status_transitions(client, db, user, session_obj, hall, transitions):
    seat_id = await _create_seat(db, hall["id"], row=4, number=len(transitions))
    booking = (await client.post(BOOKINGS, json={
        "user_id": user["id"], "session_id": session_obj["id"], "seat_id": seat_id,
    })).json()

    for status in transitions:
        resp = await client.put(f"{BOOKINGS}{booking['id']}", json={"status": status})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == status
        if status == "confirmed":
            assert data["paid_at"] is not None
        elif status == "cancelled":
            assert data["paid_at"] is None


# ============================================================
# Scenario 5: Session status change does not cascade to bookings
# ============================================================

async def test_cancel_session_bookings_remain(client, db, user, movie, hall):
    session = (await client.post(SESSIONS, json={
        "movie_id": movie["id"], "hall_id": hall["id"],
        "start_time": "2026-08-01T20:00:00", "price": 20.0, "status": "scheduled",
    })).json()
    seat_id = await _create_seat(db, hall["id"], row=5, number=1)
    booking = (await client.post(BOOKINGS, json={
        "user_id": user["id"], "session_id": session["id"], "seat_id": seat_id,
    })).json()

    # Cancel the session
    resp = await client.put(f"{SESSIONS}{session['id']}", json={"status": "cancelled"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"

    # Booking still exists and still has its original status
    resp = await client.get(f"{BOOKINGS}{booking['id']}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "pending"


# ============================================================
# Scenario 6: Booking nested response reflects correct movie data
# ============================================================

async def test_booking_response_contains_correct_movie_data(client, db):
    genre  = (await client.post(GENRES, json={"name": "Sci-Fi"})).json()
    actor  = (await client.post(ACTORS, json={"name": "Keanu Reeves", "age": 59, "gender": "male"})).json()
    movie  = (await client.post(MOVIES, json={
        "title": "The Matrix", "duration": 136, "year": 1999,
        "actor_ids": [actor["id"]], "genre_ids": [genre["id"]],
    })).json()
    hall   = (await client.post(HALLS, json={"name": "Hall B", "capacity": 80, "hall_type": "IMAX"})).json()
    session = (await client.post(SESSIONS, json={
        "movie_id": movie["id"], "hall_id": hall["id"],
        "start_time": "2026-09-01T21:00:00", "price": 25.0, "status": "scheduled",
    })).json()
    user   = (await client.post(USERS, json={"username": "neo", "email": "neo@matrix.com", "password": "redpill"})).json()
    seat_id = await _create_seat(db, hall["id"], row=1, number=1)

    booking = (await client.post(BOOKINGS, json={
        "user_id": user["id"], "session_id": session["id"], "seat_id": seat_id,
    })).json()

    resp = await client.get(f"{BOOKINGS}{booking['id']}")
    assert resp.status_code == 200
    data = resp.json()

    assert data["session"]["movie"]["title"] == "The Matrix"
    assert data["session"]["movie"]["year"] == 1999
    assert data["session"]["hall"]["hall_type"] == "IMAX"
    assert any(a["name"] == "Keanu Reeves" for a in data["session"]["movie"]["actors"])
    assert any(g["name"] == "Sci-Fi" for g in data["session"]["movie"]["genres"])


# ============================================================
# Scenario 7: Double-booking same seat in same session is rejected
# ============================================================

async def test_double_booking_same_seat_rejected(client, db, user, session_obj, hall):
    seat_id = await _create_seat(db, hall["id"], row=7, number=1)

    r1 = await client.post(BOOKINGS, json={
        "user_id": user["id"], "session_id": session_obj["id"], "seat_id": seat_id,
    })
    assert r1.status_code == 201

    # Second booking for the same seat in the same session must fail
    r2 = await client.post(BOOKINGS, json={
        "user_id": user["id"], "session_id": session_obj["id"], "seat_id": seat_id,
    })
    assert r2.status_code == 500  # IntegrityError → DatabaseError → 500


# ============================================================
# Scenario 8: Delete booking — no longer accessible
# ============================================================

async def test_delete_booking_removes_from_user_history(client, db, user, session_obj, hall):
    seat_id = await _create_seat(db, hall["id"], row=6, number=1)
    booking = (await client.post(BOOKINGS, json={
        "user_id": user["id"], "session_id": session_obj["id"], "seat_id": seat_id,
    })).json()

    # Verify booking is in user history
    history = (await client.get(f"{BOOKINGS}user/{user['id']}")).json()
    assert any(b["id"] == booking["id"] for b in history)

    # Delete booking
    assert (await client.delete(f"{BOOKINGS}{booking['id']}")).status_code == 204

    # No longer accessible by ID
    assert (await client.get(f"{BOOKINGS}{booking['id']}")).status_code == 404

    # No longer in user history
    history = (await client.get(f"{BOOKINGS}user/{user['id']}")).json()
    assert not any(b["id"] == booking["id"] for b in history)

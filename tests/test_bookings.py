import pytest

URL = "/api/v1/bookings"


async def test_create_booking(client, user, session_obj, seat):
    resp = await client.post(f"{URL}/", json={
        "user_id": user["id"],
        "session_id": session_obj["id"],
        "seat_id": seat["id"],
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["user_id"] == user["id"]
    assert data["session_id"] == session_obj["id"]
    assert data["seat_id"] == seat["id"]
    assert data["status"] == "pending"
    assert data["paid_at"] is None


async def test_booking_nested_response(client, booking):
    resp = await client.get(f"{URL}/{booking['id']}")
    data = resp.json()
    assert "session" in data
    assert "seat" in data
    assert "movie" in data["session"]
    assert "hall" in data["session"]


async def test_get_booking_by_id(client, booking):
    resp = await client.get(f"{URL}/{booking['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == booking["id"]


@pytest.mark.parametrize("booking_id", [999, 0, -1])
async def test_get_booking_not_found(client, booking_id):
    resp = await client.get(f"{URL}/{booking_id}")
    assert resp.status_code == 404


async def test_get_bookings_by_user(client, booking, user):
    resp = await client.get(f"{URL}/user/{user['id']}")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["user_id"] == user["id"]


async def test_get_bookings_by_user_empty(client):
    resp = await client.get(f"{URL}/user/9999")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_get_bookings_by_session(client, booking, session_obj):
    resp = await client.get(f"{URL}/session/{session_obj['id']}")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["session_id"] == session_obj["id"]


async def test_get_bookings_by_session_empty(client):
    resp = await client.get(f"{URL}/session/9999")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.parametrize("status", ["confirmed", "cancelled", "pending"])
async def test_update_booking_status(client, booking, status):
    resp = await client.put(f"{URL}/{booking['id']}", json={"status": status})
    assert resp.status_code == 200
    assert resp.json()["status"] == status


async def test_update_booking_confirmed_sets_paid_at(client, booking):
    resp = await client.put(f"{URL}/{booking['id']}", json={"status": "confirmed"})
    assert resp.status_code == 200
    assert resp.json()["paid_at"] is not None


async def test_update_booking_cancelled_no_paid_at(client, booking):
    resp = await client.put(f"{URL}/{booking['id']}", json={"status": "cancelled"})
    assert resp.status_code == 200
    assert resp.json()["paid_at"] is None


async def test_update_booking_not_found(client):
    resp = await client.put(f"{URL}/999", json={"status": "confirmed"})
    assert resp.status_code == 404


async def test_delete_booking(client, booking):
    resp = await client.delete(f"{URL}/{booking['id']}")
    assert resp.status_code == 204
    assert (await client.get(f"{URL}/{booking['id']}")).status_code == 404


async def test_delete_booking_not_found(client):
    resp = await client.delete(f"{URL}/999")
    assert resp.status_code == 404


async def test_multiple_bookings_same_user(client, user, session_obj, db, hall):
    from app.crud.seat import create_seat
    from app.schemas.seat import SeatCreate

    seat2 = await create_seat(db, SeatCreate(hall_id=hall["id"], row=2, number=1))
    seat3 = await create_seat(db, SeatCreate(hall_id=hall["id"], row=3, number=1))

    for seat_id in [seat2.id, seat3.id]:
        resp = await client.post(f"{URL}/", json={
            "user_id": user["id"],
            "session_id": session_obj["id"],
            "seat_id": seat_id,
        })
        assert resp.status_code == 201

    resp = await client.get(f"{URL}/user/{user['id']}")
    assert len(resp.json()) == 2

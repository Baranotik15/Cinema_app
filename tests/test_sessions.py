import pytest

URL = "/api/v1/sessions"


async def test_create_session(client, movie, hall):
    resp = await client.post(f"{URL}/", json={
        "movie_id": movie["id"], "hall_id": hall["id"],
        "start_time": "2026-06-15T14:00:00", "price": 12.5, "status": "scheduled",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["price"] == 12.5
    assert data["movie"]["id"] == movie["id"]
    assert data["hall"]["id"] == hall["id"]


@pytest.mark.parametrize("price,status", [
    (10.0,  "scheduled"),
    (25.0,  "ongoing"),
    (50.0,  "finished"),
    (0.0,   "cancelled"),
])
async def test_create_session_status_price(client, movie, hall, price, status):
    resp = await client.post(f"{URL}/", json={
        "movie_id": movie["id"], "hall_id": hall["id"],
        "start_time": "2026-06-15T10:00:00", "price": price, "status": status,
    })
    assert resp.status_code == 201
    assert resp.json()["price"] == price
    assert resp.json()["status"] == status


async def test_session_nested_movie_actors_genres(client, session_obj, movie, actor, genre):
    resp = await client.get(f"{URL}/{session_obj['id']}")
    data = resp.json()
    assert "movie" in data
    assert "hall" in data
    assert "actors" in data["movie"]
    assert "genres" in data["movie"]
    assert data["movie"]["actors"][0]["id"] == actor["id"]
    assert data["movie"]["genres"][0]["id"] == genre["id"]


async def test_list_sessions_empty(client):
    resp = await client.get(f"{URL}/")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_sessions_count(client, movie, hall):
    for i in range(3):
        await client.post(f"{URL}/", json={
            "movie_id": movie["id"], "hall_id": hall["id"],
            "start_time": f"2026-06-{15 + i}T14:00:00", "price": 10.0, "status": "scheduled",
        })
    assert len((await client.get(f"{URL}/")).json()) == 3


@pytest.mark.parametrize("skip,limit,expected", [
    (0, 10, 3),
    (0, 2,  2),
    (1, 10, 2),
])
async def test_list_sessions_pagination(client, movie, hall, skip, limit, expected):
    for i in range(3):
        await client.post(f"{URL}/", json={
            "movie_id": movie["id"], "hall_id": hall["id"],
            "start_time": f"2026-06-{15 + i}T10:00:00", "price": 10.0, "status": "scheduled",
        })
    resp = await client.get(f"{URL}/", params={"skip": skip, "limit": limit})
    assert len(resp.json()) == expected


async def test_get_session_by_id(client, session_obj):
    resp = await client.get(f"{URL}/{session_obj['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == session_obj["id"]


@pytest.mark.parametrize("session_id", [999, 0, -1])
async def test_get_session_not_found(client, session_id):
    resp = await client.get(f"{URL}/{session_id}")
    assert resp.status_code == 404


async def test_get_sessions_by_movie(client, movie, hall):
    await client.post(f"{URL}/", json={
        "movie_id": movie["id"], "hall_id": hall["id"],
        "start_time": "2026-06-15T14:00:00", "price": 10.0, "status": "scheduled",
    })
    resp = await client.get(f"{URL}/movie/{movie['id']}")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
    assert all(s["movie"]["id"] == movie["id"] for s in resp.json())


async def test_get_sessions_by_movie_empty(client, movie):
    resp = await client.get(f"{URL}/movie/{movie['id']}")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_get_sessions_by_hall(client, movie, hall):
    await client.post(f"{URL}/", json={
        "movie_id": movie["id"], "hall_id": hall["id"],
        "start_time": "2026-06-15T14:00:00", "price": 10.0, "status": "scheduled",
    })
    resp = await client.get(f"{URL}/hall/{hall['id']}")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
    assert all(s["hall"]["id"] == hall["id"] for s in resp.json())


async def test_get_sessions_by_hall_empty(client, hall):
    resp = await client.get(f"{URL}/hall/{hall['id']}")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.parametrize("new_status", ["ongoing", "finished", "cancelled"])
async def test_update_session_status(client, session_obj, new_status):
    resp = await client.put(f"{URL}/{session_obj['id']}", json={"status": new_status})
    assert resp.status_code == 200
    assert resp.json()["status"] == new_status


async def test_update_session_price(client, session_obj):
    resp = await client.put(f"{URL}/{session_obj['id']}", json={"price": 99.99})
    assert resp.status_code == 200
    assert resp.json()["price"] == 99.99


async def test_update_session_not_found(client):
    resp = await client.put(f"{URL}/999", json={"price": 10.0})
    assert resp.status_code == 404


async def test_delete_session(client, session_obj):
    resp = await client.delete(f"{URL}/{session_obj['id']}")
    assert resp.status_code == 204
    assert (await client.get(f"{URL}/{session_obj['id']}")).status_code == 404


async def test_delete_session_not_found(client):
    resp = await client.delete(f"{URL}/999")
    assert resp.status_code == 404

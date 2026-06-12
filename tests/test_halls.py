import pytest

URL = "/api/v1/halls"


@pytest.mark.parametrize("hall_type", ["2D", "3D", "IMAX"])
async def test_create_hall_types(client, hall_type):
    resp = await client.post(f"{URL}/", json={
        "name": f"Hall {hall_type}", "capacity": 100, "hall_type": hall_type,
    })
    assert resp.status_code == 201
    assert resp.json()["hall_type"] == hall_type


@pytest.mark.parametrize("capacity", [40, 100, 200, 500])
async def test_create_hall_capacity(client, capacity):
    resp = await client.post(f"{URL}/", json={
        "name": f"Hall {capacity}", "capacity": capacity, "hall_type": "2D",
    })
    assert resp.status_code == 201
    assert resp.json()["capacity"] == capacity


async def test_hall_response_schema(client):
    resp = await client.post(f"{URL}/", json={"name": "H1", "capacity": 50, "hall_type": "2D"})
    assert {"id", "name", "capacity", "hall_type"}.issubset(resp.json().keys())


async def test_create_hall_duplicate_name(client):
    await client.post(f"{URL}/", json={"name": "Hall 1", "capacity": 100, "hall_type": "2D"})
    resp = await client.post(f"{URL}/", json={"name": "Hall 1", "capacity": 50, "hall_type": "3D"})
    assert resp.status_code == 409


async def test_list_halls_empty(client):
    resp = await client.get(f"{URL}/")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_halls_count(client):
    for i, t in enumerate(["2D", "3D", "IMAX"]):
        await client.post(f"{URL}/", json={"name": f"Hall {i}", "capacity": 100, "hall_type": t})
    assert len((await client.get(f"{URL}/")).json()) == 3


@pytest.mark.parametrize("skip,limit,expected", [
    (0, 10, 3),
    (0, 2,  2),
    (1, 10, 2),
])
async def test_list_halls_pagination(client, skip, limit, expected):
    for i in range(3):
        await client.post(f"{URL}/", json={"name": f"H{i}", "capacity": 100, "hall_type": "2D"})
    resp = await client.get(f"{URL}/", params={"skip": skip, "limit": limit})
    assert len(resp.json()) == expected


async def test_get_hall_by_id(client, hall):
    resp = await client.get(f"{URL}/{hall['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == hall["id"]
    assert resp.json()["name"] == hall["name"]


@pytest.mark.parametrize("hall_id", [999, 0, -1])
async def test_get_hall_not_found(client, hall_id):
    resp = await client.get(f"{URL}/{hall_id}")
    assert resp.status_code == 404


@pytest.mark.parametrize("field,value", [
    ("name",      "Updated Hall"),
    ("capacity",  250),
    ("hall_type", "3D"),
])
async def test_update_hall_field(client, hall, field, value):
    resp = await client.put(f"{URL}/{hall['id']}", json={field: value})
    assert resp.status_code == 200
    assert resp.json()[field] == value


async def test_update_hall_not_found(client):
    resp = await client.put(f"{URL}/999", json={"name": "Ghost"})
    assert resp.status_code == 404


async def test_delete_hall(client, hall):
    resp = await client.delete(f"{URL}/{hall['id']}")
    assert resp.status_code == 204
    assert (await client.get(f"{URL}/{hall['id']}")).status_code == 404


async def test_delete_hall_not_found(client):
    resp = await client.delete(f"{URL}/999")
    assert resp.status_code == 404

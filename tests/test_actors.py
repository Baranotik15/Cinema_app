import pytest

URL = "/api/v1/actors"


@pytest.mark.parametrize("name,age,gender", [
    ("Tom Hanks",           65, "male"),
    ("Scarlett Johansson",  38, "female"),
    ("Morgan Freeman",      86, "male"),
])
async def test_create_actor(client, name, age, gender):
    resp = await client.post(f"{URL}/", json={"name": name, "age": age, "gender": gender})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == name
    assert data["age"] == age
    assert data["gender"] == gender


async def test_create_actor_minimal(client):
    resp = await client.post(f"{URL}/", json={"name": "Minimal Actor"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Minimal Actor"
    assert data["bio"] is None
    assert data["age"] is None
    assert data["gender"] is None
    assert data["image_url"] is None


async def test_actor_response_schema(client):
    resp = await client.post(f"{URL}/", json={"name": "Schema Test"})
    assert set(resp.json().keys()) == {"id", "name", "bio", "age", "gender", "image_url"}


async def test_list_actors_empty(client):
    resp = await client.get(f"{URL}/")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_actors_count(client):
    for name in ["Actor A", "Actor B", "Actor C"]:
        await client.post(f"{URL}/", json={"name": name})
    resp = await client.get(f"{URL}/")
    assert len(resp.json()) == 3


@pytest.mark.parametrize("skip,limit,expected", [
    (0, 5, 3),
    (0, 2, 2),
    (1, 5, 2),
    (2, 5, 1),
])
async def test_list_actors_pagination(client, skip, limit, expected):
    for name in ["A", "B", "C"]:
        await client.post(f"{URL}/", json={"name": name})
    resp = await client.get(f"{URL}/", params={"skip": skip, "limit": limit})
    assert resp.status_code == 200
    assert len(resp.json()) == expected


async def test_get_actor_by_id(client, actor):
    resp = await client.get(f"{URL}/{actor['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == actor["id"]
    assert resp.json()["name"] == actor["name"]


@pytest.mark.parametrize("actor_id", [999, 0, -1])
async def test_get_actor_not_found(client, actor_id):
    resp = await client.get(f"{URL}/{actor_id}")
    assert resp.status_code == 404


@pytest.mark.parametrize("field,value", [
    ("bio",       "Updated bio text"),
    ("age",       50),
    ("gender",    "female"),
    ("image_url", "https://placehold.co/100x100/png"),
    ("name",      "New Name"),
])
async def test_update_actor_field(client, actor, field, value):
    resp = await client.put(f"{URL}/{actor['id']}", json={field: value})
    assert resp.status_code == 200
    assert resp.json()[field] == value
    assert resp.json()["id"] == actor["id"]


async def test_update_actor_not_found(client):
    resp = await client.put(f"{URL}/999", json={"name": "Ghost"})
    assert resp.status_code == 404


async def test_delete_actor(client, actor):
    resp = await client.delete(f"{URL}/{actor['id']}")
    assert resp.status_code == 204
    assert (await client.get(f"{URL}/{actor['id']}")).status_code == 404


async def test_delete_actor_not_found(client):
    resp = await client.delete(f"{URL}/999")
    assert resp.status_code == 404

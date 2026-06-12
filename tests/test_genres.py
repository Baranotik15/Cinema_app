import pytest

URL = "/api/v1/genres"


@pytest.mark.parametrize("name", ["Action", "Drama", "Comedy", "Thriller", "Sci-Fi", "Horror"])
async def test_create_genre(client, name):
    resp = await client.post(f"{URL}/", json={"name": name})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == name
    assert isinstance(data["id"], int)


async def test_genre_response_schema(client):
    resp = await client.post(f"{URL}/", json={"name": "Action"})
    assert set(resp.json().keys()) == {"id", "name"}


async def test_list_genres_empty(client):
    resp = await client.get(f"{URL}/")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_genres_count(client):
    for name in ["Action", "Drama", "Comedy"]:
        await client.post(f"{URL}/", json={"name": name})
    resp = await client.get(f"{URL}/")
    assert resp.status_code == 200
    assert len(resp.json()) == 3


@pytest.mark.parametrize("skip,limit,expected", [
    (0, 10, 3),
    (0, 2,  2),
    (1, 10, 2),
    (2, 10, 1),
    (3, 10, 0),
])
async def test_list_genres_pagination(client, skip, limit, expected):
    for name in ["Action", "Drama", "Comedy"]:
        await client.post(f"{URL}/", json={"name": name})
    resp = await client.get(f"{URL}/", params={"skip": skip, "limit": limit})
    assert resp.status_code == 200
    assert len(resp.json()) == expected


async def test_get_genre_by_id(client, genre):
    resp = await client.get(f"{URL}/{genre['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == genre["id"]
    assert resp.json()["name"] == genre["name"]


@pytest.mark.parametrize("genre_id", [999, 0, -1, 12345])
async def test_get_genre_not_found(client, genre_id):
    resp = await client.get(f"{URL}/{genre_id}")
    assert resp.status_code == 404


async def test_create_genre_duplicate(client):
    await client.post(f"{URL}/", json={"name": "Action"})
    resp = await client.post(f"{URL}/", json={"name": "Action"})
    assert resp.status_code == 409


@pytest.mark.parametrize("new_name", ["Updated", "Completely Different", "New Name 123"])
async def test_update_genre(client, genre, new_name):
    resp = await client.put(f"{URL}/{genre['id']}", json={"name": new_name})
    assert resp.status_code == 200
    assert resp.json()["name"] == new_name
    assert resp.json()["id"] == genre["id"]


async def test_update_genre_not_found(client):
    resp = await client.put(f"{URL}/999", json={"name": "Ghost"})
    assert resp.status_code == 404


async def test_update_genre_duplicate_name(client):
    g1 = (await client.post(f"{URL}/", json={"name": "Action"})).json()
    await client.post(f"{URL}/", json={"name": "Drama"})
    resp = await client.put(f"{URL}/{g1['id']}", json={"name": "Drama"})
    assert resp.status_code == 409


async def test_delete_genre(client, genre):
    resp = await client.delete(f"{URL}/{genre['id']}")
    assert resp.status_code == 204
    assert (await client.get(f"{URL}/{genre['id']}")).status_code == 404


async def test_delete_genre_not_found(client):
    resp = await client.delete(f"{URL}/999")
    assert resp.status_code == 404


async def test_genre_persists_after_create(client):
    created = (await client.post(f"{URL}/", json={"name": "Sci-Fi"})).json()
    fetched = (await client.get(f"{URL}/{created['id']}")).json()
    assert fetched["name"] == "Sci-Fi"

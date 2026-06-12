import pytest

URL = "/api/v1/movies"


@pytest.mark.parametrize("title,year,rating,duration", [
    ("Inception",    2010, 8.8, 148),
    ("Forrest Gump", 1994, 8.8, 142),
    ("The Matrix",   1999, 8.7, 136),
])
async def test_create_movie(client, genre, actor, title, year, rating, duration):
    resp = await client.post(f"{URL}/", json={
        "title": title, "year": year, "rating": rating, "duration": duration,
        "actor_ids": [actor["id"]], "genre_ids": [genre["id"]],
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == title
    assert data["year"] == year
    assert data["rating"] == rating


async def test_create_movie_minimal(client):
    resp = await client.post(f"{URL}/", json={"title": "Minimal Movie"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Minimal Movie"
    assert data["actors"] == []
    assert data["genres"] == []
    assert data["rating"] == 0.0


async def test_movie_response_schema(client):
    resp = await client.post(f"{URL}/", json={"title": "Schema Movie"})
    keys = set(resp.json().keys())
    assert {"id", "title", "actors", "genres", "rating"}.issubset(keys)


async def test_movie_nested_actors_genres(client, movie, genre, actor):
    resp = await client.get(f"{URL}/{movie['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["actors"]) == 1
    assert data["actors"][0]["id"] == actor["id"]
    assert len(data["genres"]) == 1
    assert data["genres"][0]["id"] == genre["id"]


async def test_list_movies_empty(client):
    resp = await client.get(f"{URL}/")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_movies_count(client):
    for title in ["A", "B", "C"]:
        await client.post(f"{URL}/", json={"title": title})
    assert len((await client.get(f"{URL}/")).json()) == 3


@pytest.mark.parametrize("skip,limit,expected", [
    (0, 10, 3),
    (0, 2,  2),
    (1, 10, 2),
])
async def test_list_movies_pagination(client, skip, limit, expected):
    for title in ["A", "B", "C"]:
        await client.post(f"{URL}/", json={"title": title})
    resp = await client.get(f"{URL}/", params={"skip": skip, "limit": limit})
    assert len(resp.json()) == expected


@pytest.mark.parametrize("movie_id", [999, 0, -1])
async def test_get_movie_not_found(client, movie_id):
    resp = await client.get(f"{URL}/{movie_id}")
    assert resp.status_code == 404


@pytest.mark.parametrize("field,value", [
    ("title",       "Updated Title"),
    ("description", "New description"),
    ("rating",      9.0),
    ("year",        2025),
    ("duration",    180),
])
async def test_update_movie_field(client, movie, field, value):
    resp = await client.put(f"{URL}/{movie['id']}", json={field: value})
    assert resp.status_code == 200
    assert resp.json()[field] == value


async def test_update_movie_actors(client, movie):
    new_actor = (await client.post("/api/v1/actors/", json={"name": "New Actor"})).json()
    resp = await client.put(f"{URL}/{movie['id']}", json={"actor_ids": [new_actor["id"]]})
    assert resp.status_code == 200
    assert new_actor["id"] in [a["id"] for a in resp.json()["actors"]]


async def test_update_movie_genres(client, movie):
    new_genre = (await client.post("/api/v1/genres/", json={"name": "Horror"})).json()
    resp = await client.put(f"{URL}/{movie['id']}", json={"genre_ids": [new_genre["id"]]})
    assert resp.status_code == 200
    assert new_genre["id"] in [g["id"] for g in resp.json()["genres"]]


async def test_update_movie_not_found(client):
    resp = await client.put(f"{URL}/999", json={"title": "Ghost"})
    assert resp.status_code == 404


async def test_delete_movie(client, movie):
    resp = await client.delete(f"{URL}/{movie['id']}")
    assert resp.status_code == 204
    assert (await client.get(f"{URL}/{movie['id']}")).status_code == 404


async def test_delete_movie_not_found(client):
    resp = await client.delete(f"{URL}/999")
    assert resp.status_code == 404

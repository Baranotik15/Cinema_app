import pytest

URL = "/api/v1/users"

BASE = {"username": "testuser", "email": "test@example.com", "password": "password123"}


async def test_create_user(client):
    resp = await client.post(f"{URL}/", json=BASE)
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == BASE["username"]
    assert data["email"] == BASE["email"]


async def test_password_not_in_response(client):
    resp = await client.post(f"{URL}/", json=BASE)
    assert "password" not in resp.json()
    assert "hashed_password" not in resp.json()


async def test_user_default_flags(client):
    resp = await client.post(f"{URL}/", json=BASE)
    data = resp.json()
    assert data["is_active"] is True
    assert data["is_admin"] is False


async def test_user_response_schema(client):
    resp = await client.post(f"{URL}/", json=BASE)
    assert {"id", "username", "email", "is_active", "is_admin"}.issubset(resp.json().keys())


@pytest.mark.parametrize("username,email", [
    ("alice", "alice@example.com"),
    ("bob",   "bob@example.com"),
    ("carol", "carol@example.com"),
])
async def test_create_multiple_users(client, username, email):
    resp = await client.post(f"{URL}/", json={"username": username, "email": email, "password": "pass123"})
    assert resp.status_code == 201
    assert resp.json()["username"] == username


async def test_create_user_duplicate_username(client):
    await client.post(f"{URL}/", json=BASE)
    resp = await client.post(f"{URL}/", json={**BASE, "email": "other@example.com"})
    assert resp.status_code == 409


async def test_create_user_duplicate_email(client):
    await client.post(f"{URL}/", json=BASE)
    resp = await client.post(f"{URL}/", json={**BASE, "username": "other_user"})
    assert resp.status_code == 409


async def test_list_users_empty(client):
    resp = await client.get(f"{URL}/")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_users_count(client):
    for i in range(3):
        await client.post(f"{URL}/", json={
            "username": f"user{i}", "email": f"user{i}@test.com", "password": "pass",
        })
    assert len((await client.get(f"{URL}/")).json()) == 3


@pytest.mark.parametrize("skip,limit,expected", [
    (0, 10, 3),
    (0, 2,  2),
    (1, 10, 2),
])
async def test_list_users_pagination(client, skip, limit, expected):
    for i in range(3):
        await client.post(f"{URL}/", json={
            "username": f"u{i}", "email": f"u{i}@test.com", "password": "pass",
        })
    resp = await client.get(f"{URL}/", params={"skip": skip, "limit": limit})
    assert len(resp.json()) == expected


async def test_get_user_by_id(client, user):
    resp = await client.get(f"{URL}/{user['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == user["id"]


@pytest.mark.parametrize("user_id", [999, 0, -1])
async def test_get_user_not_found(client, user_id):
    resp = await client.get(f"{URL}/{user_id}")
    assert resp.status_code == 404


@pytest.mark.parametrize("field,value", [
    ("username", "updated_user"),
    ("email",    "updated@example.com"),
])
async def test_update_user_field(client, user, field, value):
    resp = await client.put(f"{URL}/{user['id']}", json={field: value})
    assert resp.status_code == 200
    assert resp.json()[field] == value


async def test_update_user_password(client, user):
    resp = await client.put(f"{URL}/{user['id']}", json={"password": "newpassword456"})
    assert resp.status_code == 200
    assert "password" not in resp.json()


async def test_update_user_not_found(client):
    resp = await client.put(f"{URL}/999", json={"username": "ghost"})
    assert resp.status_code == 404


async def test_delete_user(client, user):
    resp = await client.delete(f"{URL}/{user['id']}")
    assert resp.status_code == 204
    assert (await client.get(f"{URL}/{user['id']}")).status_code == 404


async def test_delete_user_not_found(client):
    resp = await client.delete(f"{URL}/999")
    assert resp.status_code == 404

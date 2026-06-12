import pytest
from app.crud.seat import (
    create_seat, create_seats_bulk, get_seat,
    get_seats_by_hall, update_seat, delete_seat,
)
from app.schemas.seat import SeatCreate, SeatUpdate
from app.exceptions import NotFoundError, DatabaseError


async def test_create_seat(db, hall):
    s = await create_seat(db, SeatCreate(hall_id=hall["id"], row=1, number=1))
    assert s.id is not None
    assert s.hall_id == hall["id"]
    assert s.row == 1
    assert s.number == 1


@pytest.mark.parametrize("row,number,seat_type", [
    (1, 1,  "standard"),
    (2, 3,  "vip"),
    (5, 10, "disabled"),
])
async def test_create_seat_types(db, hall, row, number, seat_type):
    s = await create_seat(db, SeatCreate(
        hall_id=hall["id"], row=row, number=number, seat_type=seat_type,
    ))
    assert s.seat_type.value == seat_type


async def test_create_seat_duplicate_raises(db, hall):
    await create_seat(db, SeatCreate(hall_id=hall["id"], row=1, number=1))
    with pytest.raises(DatabaseError):
        await create_seat(db, SeatCreate(hall_id=hall["id"], row=1, number=1))


async def test_create_seats_bulk(db, hall):
    data = [
        SeatCreate(hall_id=hall["id"], row=r, number=n)
        for r in range(1, 4)
        for n in range(1, 4)
    ]
    seats = await create_seats_bulk(db, data)
    assert len(seats) == 9


async def test_create_seats_bulk_duplicate_raises(db, hall):
    await create_seat(db, SeatCreate(hall_id=hall["id"], row=1, number=1))
    with pytest.raises(DatabaseError):
        await create_seats_bulk(db, [
            SeatCreate(hall_id=hall["id"], row=1, number=1),
            SeatCreate(hall_id=hall["id"], row=1, number=2),
        ])


async def test_get_seat(db, hall):
    created = await create_seat(db, SeatCreate(hall_id=hall["id"], row=1, number=1))
    found = await get_seat(db, created.id)
    assert found is not None
    assert found.id == created.id


async def test_get_seat_not_found(db):
    assert await get_seat(db, 999) is None


async def test_get_seats_by_hall(db, hall):
    for n in range(1, 4):
        await create_seat(db, SeatCreate(hall_id=hall["id"], row=1, number=n))
    seats = await get_seats_by_hall(db, hall["id"])
    assert len(seats) == 3


async def test_get_seats_by_hall_empty(db, hall):
    assert await get_seats_by_hall(db, hall["id"]) == []


@pytest.mark.parametrize("field,value", [
    ("row",       5),
    ("number",    10),
    ("seat_type", "vip"),
])
async def test_update_seat_field(db, hall, field, value):
    s = await create_seat(db, SeatCreate(hall_id=hall["id"], row=1, number=1))
    updated = await update_seat(db, s.id, SeatUpdate(**{field: value}))
    if field == "seat_type":
        assert updated.seat_type.value == value
    else:
        assert getattr(updated, field) == value


async def test_update_seat_not_found(db):
    with pytest.raises(NotFoundError):
        await update_seat(db, 999, SeatUpdate(row=1))


async def test_delete_seat(db, hall):
    s = await create_seat(db, SeatCreate(hall_id=hall["id"], row=1, number=1))
    result = await delete_seat(db, s.id)
    assert result is True
    assert await get_seat(db, s.id) is None


async def test_delete_seat_not_found(db):
    with pytest.raises(NotFoundError):
        await delete_seat(db, 999)

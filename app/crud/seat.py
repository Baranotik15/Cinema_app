from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.seat import Seat
from app.schemas.seat import SeatCreate, SeatUpdate
from app.exceptions import NotFoundError, DatabaseError


async def get_seat(db: AsyncSession, seat_id: int) -> Seat | None:
    try:
        result = await db.execute(select(Seat).where(Seat.id == seat_id))
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        raise DatabaseError(str(e))


async def get_seats_by_hall(db: AsyncSession, hall_id: int) -> list[Seat]:
    try:
        result = await db.execute(select(Seat).where(Seat.hall_id == hall_id))
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise DatabaseError(str(e))


async def create_seat(db: AsyncSession, data: SeatCreate) -> Seat:
    try:
        seat = Seat(**data.model_dump())
        db.add(seat)
        await db.commit()
        await db.refresh(seat)
        return seat
    except IntegrityError:
        await db.rollback()
        raise DatabaseError("Seat with this row and number already exists in the hall")
    except SQLAlchemyError as e:
        await db.rollback()
        raise DatabaseError(str(e))


async def create_seats_bulk(db: AsyncSession, seats: list[SeatCreate]) -> list[Seat]:
    try:
        db_seats = [Seat(**seat.model_dump()) for seat in seats]
        db.add_all(db_seats)
        await db.commit()
        return db_seats
    except IntegrityError:
        await db.rollback()
        raise DatabaseError("One or more seats already exist in the hall")
    except SQLAlchemyError as e:
        await db.rollback()
        raise DatabaseError(str(e))


async def update_seat(db: AsyncSession, seat_id: int, data: SeatUpdate) -> Seat:
    try:
        seat = await get_seat(db, seat_id)
        if not seat:
            raise NotFoundError("Seat", seat_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(seat, field, value)
        await db.commit()
        await db.refresh(seat)
        return seat
    except (NotFoundError, DatabaseError):
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        raise DatabaseError(str(e))


async def delete_seat(db: AsyncSession, seat_id: int) -> bool:
    try:
        seat = await get_seat(db, seat_id)
        if not seat:
            raise NotFoundError("Seat", seat_id)
        await db.delete(seat)
        await db.commit()
        return True
    except NotFoundError:
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        raise DatabaseError(str(e))

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.booking import Booking
from app.schemas.booking import BookingCreate, BookingUpdate
from app.enums import BookingStatus
from app.exceptions import NotFoundError, DatabaseError


async def get_booking(db: AsyncSession, booking_id: int) -> Booking | None:
    try:
        result = await db.execute(
            select(Booking)
            .options(
                selectinload(Booking.session),
                selectinload(Booking.seat),
            )
            .where(Booking.id == booking_id)
        )
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        raise DatabaseError(str(e))


async def get_bookings_by_user(db: AsyncSession, user_id: int) -> list[Booking]:
    try:
        result = await db.execute(
            select(Booking)
            .options(selectinload(Booking.session), selectinload(Booking.seat))
            .where(Booking.user_id == user_id)
        )
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise DatabaseError(str(e))


async def get_bookings_by_session(db: AsyncSession, session_id: int) -> list[Booking]:
    try:
        result = await db.execute(
            select(Booking)
            .options(selectinload(Booking.seat))
            .where(Booking.session_id == session_id)
        )
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise DatabaseError(str(e))


async def create_booking(db: AsyncSession, data: BookingCreate) -> Booking:
    try:
        booking = Booking(**data.model_dump())
        db.add(booking)
        await db.commit()
        await db.refresh(booking)
        return await get_booking(db, booking.id)
    except IntegrityError:
        await db.rollback()
        raise DatabaseError("Booking failed: seat is already taken or invalid ids")
    except SQLAlchemyError as e:
        await db.rollback()
        raise DatabaseError(str(e))


async def update_booking(db: AsyncSession, booking_id: int, data: BookingUpdate) -> Booking:
    try:
        booking = await get_booking(db, booking_id)
        if not booking:
            raise NotFoundError("Booking", booking_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(booking, field, value)
        if data.status == BookingStatus.confirmed:
            booking.paid_at = datetime.utcnow()
        await db.commit()
        return await get_booking(db, booking_id)
    except (NotFoundError, DatabaseError):
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        raise DatabaseError(str(e))


async def delete_booking(db: AsyncSession, booking_id: int) -> bool:
    try:
        booking = await get_booking(db, booking_id)
        if not booking:
            raise NotFoundError("Booking", booking_id)
        await db.delete(booking)
        await db.commit()
        return True
    except NotFoundError:
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        raise DatabaseError(str(e))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.hall import Hall
from app.schemas.hall import HallCreate, HallUpdate
from app.exceptions import NotFoundError, AlreadyExistsError, DatabaseError


async def get_hall(db: AsyncSession, hall_id: int) -> Hall | None:
    try:
        result = await db.execute(
            select(Hall)
            .options(selectinload(Hall.seats))
            .where(Hall.id == hall_id)
        )
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        raise DatabaseError(str(e))


async def get_halls(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Hall]:
    try:
        result = await db.execute(select(Hall).offset(skip).limit(limit))
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise DatabaseError(str(e))


async def create_hall(db: AsyncSession, data: HallCreate) -> Hall:
    try:
        hall = Hall(**data.model_dump())
        db.add(hall)
        await db.commit()
        await db.refresh(hall)
        return hall
    except IntegrityError:
        await db.rollback()
        raise AlreadyExistsError("Hall", "name", data.name)
    except SQLAlchemyError as e:
        await db.rollback()
        raise DatabaseError(str(e))


async def update_hall(db: AsyncSession, hall_id: int, data: HallUpdate) -> Hall:
    try:
        hall = await get_hall(db, hall_id)
        if not hall:
            raise NotFoundError("Hall", hall_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(hall, field, value)
        await db.commit()
        await db.refresh(hall)
        return hall
    except (NotFoundError, DatabaseError):
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        raise DatabaseError(str(e))


async def delete_hall(db: AsyncSession, hall_id: int) -> bool:
    try:
        hall = await get_hall(db, hall_id)
        if not hall:
            raise NotFoundError("Hall", hall_id)
        await db.delete(hall)
        await db.commit()
        return True
    except NotFoundError:
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        raise DatabaseError(str(e))

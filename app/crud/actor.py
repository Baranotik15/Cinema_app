from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.actor import Actor
from app.schemas.actor import ActorCreate, ActorUpdate
from app.exceptions import NotFoundError, AlreadyExistsError, DatabaseError


async def get_actor(db: AsyncSession, actor_id: int) -> Actor | None:
    try:
        result = await db.execute(select(Actor).where(Actor.id == actor_id))
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        raise DatabaseError(str(e))


async def get_actors(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Actor]:
    try:
        result = await db.execute(select(Actor).offset(skip).limit(limit))
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise DatabaseError(str(e))


async def create_actor(db: AsyncSession, data: ActorCreate) -> Actor:
    try:
        actor = Actor(**data.model_dump())
        db.add(actor)
        await db.commit()
        await db.refresh(actor)
        return actor
    except IntegrityError:
        await db.rollback()
        raise AlreadyExistsError("Actor", "name", data.name)
    except SQLAlchemyError as e:
        await db.rollback()
        raise DatabaseError(str(e))


async def update_actor(db: AsyncSession, actor_id: int, data: ActorUpdate) -> Actor:
    try:
        actor = await get_actor(db, actor_id)
        if not actor:
            raise NotFoundError("Actor", actor_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(actor, field, value)
        await db.commit()
        await db.refresh(actor)
        return actor
    except (NotFoundError, DatabaseError):
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        raise DatabaseError(str(e))


async def delete_actor(db: AsyncSession, actor_id: int) -> bool:
    try:
        actor = await get_actor(db, actor_id)
        if not actor:
            raise NotFoundError("Actor", actor_id)
        await db.delete(actor)
        await db.commit()
        return True
    except NotFoundError:
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        raise DatabaseError(str(e))

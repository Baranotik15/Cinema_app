from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.session import Session
from app.schemas.session import SessionCreate, SessionUpdate
from app.exceptions import NotFoundError, DatabaseError


async def get_session(db: AsyncSession, session_id: int) -> Session | None:
    try:
        result = await db.execute(
            select(Session)
            .options(selectinload(Session.movie), selectinload(Session.hall))
            .where(Session.id == session_id)
        )
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        raise DatabaseError(str(e))


async def get_sessions(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Session]:
    try:
        result = await db.execute(
            select(Session)
            .options(selectinload(Session.movie), selectinload(Session.hall))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise DatabaseError(str(e))


async def get_sessions_by_movie(db: AsyncSession, movie_id: int) -> list[Session]:
    try:
        result = await db.execute(
            select(Session)
            .options(selectinload(Session.hall))
            .where(Session.movie_id == movie_id)
        )
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise DatabaseError(str(e))


async def get_sessions_by_hall(db: AsyncSession, hall_id: int) -> list[Session]:
    try:
        result = await db.execute(
            select(Session)
            .options(selectinload(Session.movie))
            .where(Session.hall_id == hall_id)
        )
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise DatabaseError(str(e))


async def create_session(db: AsyncSession, data: SessionCreate) -> Session:
    try:
        session = Session(**data.model_dump())
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return await get_session(db, session.id)
    except IntegrityError:
        await db.rollback()
        raise DatabaseError("Session creation failed: invalid movie_id or hall_id")
    except SQLAlchemyError as e:
        await db.rollback()
        raise DatabaseError(str(e))


async def update_session(db: AsyncSession, session_id: int, data: SessionUpdate) -> Session:
    try:
        session = await get_session(db, session_id)
        if not session:
            raise NotFoundError("Session", session_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(session, field, value)
        await db.commit()
        return await get_session(db, session_id)
    except (NotFoundError, DatabaseError):
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        raise DatabaseError(str(e))


async def delete_session(db: AsyncSession, session_id: int) -> bool:
    try:
        session = await get_session(db, session_id)
        if not session:
            raise NotFoundError("Session", session_id)
        await db.delete(session)
        await db.commit()
        return True
    except NotFoundError:
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        raise DatabaseError(str(e))

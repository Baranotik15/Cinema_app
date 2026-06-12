from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.genre import Genre
from app.schemas.genre import GenreCreate, GenreUpdate
from app.exceptions import NotFoundError, AlreadyExistsError, DatabaseError


async def get_genre(db: AsyncSession, genre_id: int) -> Genre | None:
    try:
        result = await db.execute(select(Genre).where(Genre.id == genre_id))
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        raise DatabaseError(str(e))


async def get_genres(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Genre]:
    try:
        result = await db.execute(select(Genre).offset(skip).limit(limit))
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise DatabaseError(str(e))


async def create_genre(db: AsyncSession, data: GenreCreate) -> Genre:
    try:
        genre = Genre(**data.model_dump())
        db.add(genre)
        await db.commit()
        await db.refresh(genre)
        return genre
    except IntegrityError:
        await db.rollback()
        raise AlreadyExistsError("Genre", "name", data.name)
    except SQLAlchemyError as e:
        await db.rollback()
        raise DatabaseError(str(e))


async def update_genre(db: AsyncSession, genre_id: int, data: GenreUpdate) -> Genre:
    try:
        genre = await get_genre(db, genre_id)
        if not genre:
            raise NotFoundError("Genre", genre_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(genre, field, value)
        await db.commit()
        await db.refresh(genre)
        return genre
    except (NotFoundError, DatabaseError):
        raise
    except IntegrityError:
        await db.rollback()
        raise AlreadyExistsError("Genre", "name", data.name)
    except SQLAlchemyError as e:
        await db.rollback()
        raise DatabaseError(str(e))


async def delete_genre(db: AsyncSession, genre_id: int) -> bool:
    try:
        genre = await get_genre(db, genre_id)
        if not genre:
            raise NotFoundError("Genre", genre_id)
        await db.delete(genre)
        await db.commit()
        return True
    except NotFoundError:
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        raise DatabaseError(str(e))

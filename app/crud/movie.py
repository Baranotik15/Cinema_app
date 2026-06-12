from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.movie import Movie
from app.models.actor import Actor
from app.models.genre import Genre
from app.schemas.movie import MovieCreate, MovieUpdate
from app.exceptions import NotFoundError, DatabaseError


async def get_movie(db: AsyncSession, movie_id: int) -> Movie | None:
    try:
        result = await db.execute(
            select(Movie)
            .options(selectinload(Movie.actors), selectinload(Movie.genres))
            .where(Movie.id == movie_id)
        )
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        raise DatabaseError(str(e))


async def get_movies(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Movie]:
    try:
        result = await db.execute(
            select(Movie)
            .options(selectinload(Movie.actors), selectinload(Movie.genres))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise DatabaseError(str(e))


async def create_movie(db: AsyncSession, data: MovieCreate) -> Movie:
    try:
        movie_data = data.model_dump(exclude={"actor_ids", "genre_ids"})
        movie = Movie(**movie_data)

        if data.actor_ids:
            result = await db.execute(select(Actor).where(Actor.id.in_(data.actor_ids)))
            movie.actors = result.scalars().all()

        if data.genre_ids:
            result = await db.execute(select(Genre).where(Genre.id.in_(data.genre_ids)))
            movie.genres = result.scalars().all()

        db.add(movie)
        await db.commit()
        await db.refresh(movie)
        return await get_movie(db, movie.id)
    except IntegrityError:
        await db.rollback()
        raise DatabaseError("Movie creation failed due to integrity error")
    except SQLAlchemyError as e:
        await db.rollback()
        raise DatabaseError(str(e))


async def update_movie(db: AsyncSession, movie_id: int, data: MovieUpdate) -> Movie:
    try:
        movie = await get_movie(db, movie_id)
        if not movie:
            raise NotFoundError("Movie", movie_id)

        for field, value in data.model_dump(exclude_unset=True, exclude={"actor_ids", "genre_ids"}).items():
            setattr(movie, field, value)

        if data.actor_ids is not None:
            result = await db.execute(select(Actor).where(Actor.id.in_(data.actor_ids)))
            movie.actors = result.scalars().all()

        if data.genre_ids is not None:
            result = await db.execute(select(Genre).where(Genre.id.in_(data.genre_ids)))
            movie.genres = result.scalars().all()

        await db.commit()
        return await get_movie(db, movie.id)
    except (NotFoundError, DatabaseError):
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        raise DatabaseError(str(e))


async def delete_movie(db: AsyncSession, movie_id: int) -> bool:
    try:
        movie = await get_movie(db, movie_id)
        if not movie:
            raise NotFoundError("Movie", movie_id)
        await db.delete(movie)
        await db.commit()
        return True
    except NotFoundError:
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        raise DatabaseError(str(e))

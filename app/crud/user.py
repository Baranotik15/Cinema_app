from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.exceptions import NotFoundError, AlreadyExistsError, DatabaseError


async def get_user(db: AsyncSession, user_id: int) -> User | None:
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        raise DatabaseError(str(e))


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    try:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        raise DatabaseError(str(e))


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    try:
        result = await db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise DatabaseError(str(e))


async def create_user(db: AsyncSession, data: UserCreate, hashed_password: str) -> User:
    try:
        user = User(
            username=data.username,
            email=data.email,
            hashed_password=hashed_password,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    except IntegrityError:
        await db.rollback()
        raise AlreadyExistsError("User", "email", data.email)
    except SQLAlchemyError as e:
        await db.rollback()
        raise DatabaseError(str(e))


async def update_user(db: AsyncSession, user_id: int, data: UserUpdate, hashed_password: str | None = None) -> User:
    try:
        user = await get_user(db, user_id)
        if not user:
            raise NotFoundError("User", user_id)
        for field, value in data.model_dump(exclude_unset=True, exclude={"password"}).items():
            setattr(user, field, value)
        if hashed_password:
            user.hashed_password = hashed_password
        await db.commit()
        await db.refresh(user)
        return user
    except (NotFoundError, DatabaseError):
        raise
    except IntegrityError:
        await db.rollback()
        raise AlreadyExistsError("User", "email", data.email)
    except SQLAlchemyError as e:
        await db.rollback()
        raise DatabaseError(str(e))


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    try:
        user = await get_user(db, user_id)
        if not user:
            raise NotFoundError("User", user_id)
        await db.delete(user)
        await db.commit()
        return True
    except NotFoundError:
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        raise DatabaseError(str(e))

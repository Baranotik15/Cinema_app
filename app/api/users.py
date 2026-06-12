from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt
from app.database import get_db
from app.crud import user as crud
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.exceptions import NotFoundError, AlreadyExistsError, DatabaseError

router = APIRouter()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


@router.get("/", response_model=list[UserResponse])
async def get_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.get_users(db, skip=skip, limit=limit)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        user = await crud.get_user(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        return user
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        hashed = hash_password(data.password)
        return await crud.create_user(db, data, hashed)
    except AlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, data: UserUpdate, db: AsyncSession = Depends(get_db)):
    try:
        hashed = hash_password(data.password) if data.password else None
        return await crud.update_user(db, user_id, data, hashed)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except AlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        await crud.delete_user(db, user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.crud import genre as crud
from app.schemas.genre import GenreCreate, GenreUpdate, GenreResponse
from app.exceptions import NotFoundError, AlreadyExistsError, DatabaseError

router = APIRouter()


@router.get("/", response_model=list[GenreResponse])
async def get_genres(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.get_genres(db, skip=skip, limit=limit)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.get("/{genre_id}", response_model=GenreResponse)
async def get_genre(genre_id: int, db: AsyncSession = Depends(get_db)):
    try:
        genre = await crud.get_genre(db, genre_id)
        if not genre:
            raise HTTPException(status_code=404, detail=f"Genre {genre_id} not found")
        return genre
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.post("/", response_model=GenreResponse, status_code=201)
async def create_genre(data: GenreCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.create_genre(db, data)
    except AlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.put("/{genre_id}", response_model=GenreResponse)
async def update_genre(genre_id: int, data: GenreUpdate, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.update_genre(db, genre_id, data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except AlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.delete("/{genre_id}", status_code=204)
async def delete_genre(genre_id: int, db: AsyncSession = Depends(get_db)):
    try:
        await crud.delete_genre(db, genre_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)

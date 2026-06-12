from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.crud import movie as crud
from app.schemas.movie import MovieCreate, MovieUpdate, MovieResponse
from app.exceptions import NotFoundError, DatabaseError

router = APIRouter()


@router.get("/", response_model=list[MovieResponse])
async def get_movies(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.get_movies(db, skip=skip, limit=limit)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.get("/{movie_id}", response_model=MovieResponse)
async def get_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    try:
        movie = await crud.get_movie(db, movie_id)
        if not movie:
            raise HTTPException(status_code=404, detail=f"Movie {movie_id} not found")
        return movie
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.post("/", response_model=MovieResponse, status_code=201)
async def create_movie(data: MovieCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.create_movie(db, data)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.put("/{movie_id}", response_model=MovieResponse)
async def update_movie(movie_id: int, data: MovieUpdate, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.update_movie(db, movie_id, data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.delete("/{movie_id}", status_code=204)
async def delete_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    try:
        await crud.delete_movie(db, movie_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)

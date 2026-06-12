from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.crud import session as crud
from app.schemas.session import SessionCreate, SessionUpdate, SessionResponse
from app.exceptions import NotFoundError, DatabaseError

router = APIRouter()


@router.get("/", response_model=list[SessionResponse])
async def get_sessions(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.get_sessions(db, skip=skip, limit=limit)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: int, db: AsyncSession = Depends(get_db)):
    try:
        session = await crud.get_session(db, session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        return session
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.get("/movie/{movie_id}", response_model=list[SessionResponse])
async def get_sessions_by_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.get_sessions_by_movie(db, movie_id)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.get("/hall/{hall_id}", response_model=list[SessionResponse])
async def get_sessions_by_hall(hall_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.get_sessions_by_hall(db, hall_id)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.post("/", response_model=SessionResponse, status_code=201)
async def create_session(data: SessionCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.create_session(db, data)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(session_id: int, data: SessionUpdate, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.update_session(db, session_id, data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.delete("/{session_id}", status_code=204)
async def delete_session(session_id: int, db: AsyncSession = Depends(get_db)):
    try:
        await crud.delete_session(db, session_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)

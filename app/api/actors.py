from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.crud import actor as crud
from app.schemas.actor import ActorCreate, ActorUpdate, ActorResponse
from app.exceptions import NotFoundError, AlreadyExistsError, DatabaseError

router = APIRouter()


@router.get("/", response_model=list[ActorResponse])
async def get_actors(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.get_actors(db, skip=skip, limit=limit)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.get("/{actor_id}", response_model=ActorResponse)
async def get_actor(actor_id: int, db: AsyncSession = Depends(get_db)):
    try:
        actor = await crud.get_actor(db, actor_id)
        if not actor:
            raise HTTPException(status_code=404, detail=f"Actor {actor_id} not found")
        return actor
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.post("/", response_model=ActorResponse, status_code=201)
async def create_actor(data: ActorCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.create_actor(db, data)
    except AlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.put("/{actor_id}", response_model=ActorResponse)
async def update_actor(actor_id: int, data: ActorUpdate, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.update_actor(db, actor_id, data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.delete("/{actor_id}", status_code=204)
async def delete_actor(actor_id: int, db: AsyncSession = Depends(get_db)):
    try:
        await crud.delete_actor(db, actor_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)

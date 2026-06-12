from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.crud import hall as crud
from app.schemas.hall import HallCreate, HallUpdate, HallResponse
from app.exceptions import NotFoundError, AlreadyExistsError, DatabaseError

router = APIRouter()


@router.get("/", response_model=list[HallResponse])
async def get_halls(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.get_halls(db, skip=skip, limit=limit)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.get("/{hall_id}", response_model=HallResponse)
async def get_hall(hall_id: int, db: AsyncSession = Depends(get_db)):
    try:
        hall = await crud.get_hall(db, hall_id)
        if not hall:
            raise HTTPException(status_code=404, detail=f"Hall {hall_id} not found")
        return hall
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.post("/", response_model=HallResponse, status_code=201)
async def create_hall(data: HallCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.create_hall(db, data)
    except AlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.put("/{hall_id}", response_model=HallResponse)
async def update_hall(hall_id: int, data: HallUpdate, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.update_hall(db, hall_id, data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except AlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.delete("/{hall_id}", status_code=204)
async def delete_hall(hall_id: int, db: AsyncSession = Depends(get_db)):
    try:
        await crud.delete_hall(db, hall_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.crud import booking as crud
from app.schemas.booking import BookingCreate, BookingUpdate, BookingResponse
from app.exceptions import NotFoundError, DatabaseError

router = APIRouter()


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(booking_id: int, db: AsyncSession = Depends(get_db)):
    try:
        booking = await crud.get_booking(db, booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")
        return booking
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.get("/user/{user_id}", response_model=list[BookingResponse])
async def get_bookings_by_user(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.get_bookings_by_user(db, user_id)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.get("/session/{session_id}", response_model=list[BookingResponse])
async def get_bookings_by_session(session_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.get_bookings_by_session(db, session_id)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.post("/", response_model=BookingResponse, status_code=201)
async def create_booking(data: BookingCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.create_booking(db, data)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(booking_id: int, data: BookingUpdate, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.update_booking(db, booking_id, data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)


@router.delete("/{booking_id}", status_code=204)
async def delete_booking(booking_id: int, db: AsyncSession = Depends(get_db)):
    try:
        await crud.delete_booking(db, booking_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)

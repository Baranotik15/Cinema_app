from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.enums import BookingStatus
from app.schemas.session import SessionResponse
from app.schemas.seat import SeatResponse


class BookingBase(BaseModel):
    user_id: int
    session_id: int
    seat_id: int


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    status: BookingStatus | None = None


class BookingResponse(BookingBase):
    id: int
    status: BookingStatus
    paid_at: datetime | None = None
    session: SessionResponse
    seat: SeatResponse

    model_config = ConfigDict(from_attributes=True)

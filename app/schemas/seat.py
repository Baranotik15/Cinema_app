from pydantic import BaseModel, ConfigDict
from app.enums import SeatType


class SeatBase(BaseModel):
    hall_id: int
    row: int
    number: int
    seat_type: SeatType = SeatType.standard


class SeatCreate(SeatBase):
    pass


class SeatUpdate(BaseModel):
    row: int | None = None
    number: int | None = None
    seat_type: SeatType | None = None


class SeatResponse(SeatBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

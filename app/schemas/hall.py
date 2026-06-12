from pydantic import BaseModel, ConfigDict
from app.enums import HallType


class HallBase(BaseModel):
    name: str
    capacity: int
    hall_type: HallType = HallType.hall_2d


class HallCreate(HallBase):
    pass


class HallUpdate(BaseModel):
    name: str | None = None
    capacity: int | None = None
    hall_type: HallType | None = None


class HallResponse(HallBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

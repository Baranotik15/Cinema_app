from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.enums import SessionStatus
from app.schemas.movie import MovieResponse
from app.schemas.hall import HallResponse


class SessionBase(BaseModel):
    movie_id: int
    hall_id: int
    start_time: datetime
    price: float
    status: SessionStatus = SessionStatus.scheduled


class SessionCreate(SessionBase):
    pass


class SessionUpdate(BaseModel):
    start_time: datetime | None = None
    price: float | None = None
    status: SessionStatus | None = None


class SessionResponse(SessionBase):
    id: int
    movie: MovieResponse
    hall: HallResponse

    model_config = ConfigDict(from_attributes=True)

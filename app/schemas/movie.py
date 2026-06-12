from pydantic import BaseModel, ConfigDict
from app.schemas.actor import ActorResponse
from app.schemas.genre import GenreResponse


class MovieBase(BaseModel):
    title: str
    description: str | None = None
    duration: int | None = None
    year: int | None = None
    rating: float = 0.0
    poster_url: str | None = None


class MovieCreate(MovieBase):
    actor_ids: list[int] = []
    genre_ids: list[int] = []


class MovieUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    duration: int | None = None
    year: int | None = None
    rating: float | None = None
    poster_url: str | None = None
    actor_ids: list[int] | None = None
    genre_ids: list[int] | None = None


class MovieResponse(MovieBase):
    id: int
    actors: list[ActorResponse] = []
    genres: list[GenreResponse] = []

    model_config = ConfigDict(from_attributes=True)

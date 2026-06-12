from pydantic import BaseModel, ConfigDict


class ActorBase(BaseModel):
    name: str
    bio: str | None = None
    age: int | None = None
    gender: str | None = None
    image_url: str | None = None


class ActorCreate(ActorBase):
    pass


class ActorUpdate(BaseModel):
    name: str | None = None
    bio: str | None = None
    age: int | None = None
    gender: str | None = None
    image_url: str | None = None


class ActorResponse(ActorBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

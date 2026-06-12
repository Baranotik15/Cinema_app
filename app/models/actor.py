from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.associations import movie_actors


class Actor(Base):
    __tablename__ = "actors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    bio = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    image_url = Column(String, nullable=True)

    movies = relationship("Movie", secondary=movie_actors, back_populates="actors")

from sqlalchemy import Column, Integer, String, Text, Float
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.associations import movie_actors, movie_genres


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    duration = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    rating = Column(Float, default=0.0)
    poster_url = Column(String, nullable=True)

    actors = relationship("Actor", secondary=movie_actors, back_populates="movies")
    genres = relationship("Genre", secondary=movie_genres, back_populates="movies")
    sessions = relationship("Session", back_populates="movie")

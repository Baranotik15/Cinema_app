from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from app.enums import SessionStatus


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    hall_id = Column(Integer, ForeignKey("halls.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    price = Column(Float, nullable=False)
    status = Column(Enum(SessionStatus), default=SessionStatus.scheduled, nullable=False)

    movie = relationship("Movie", back_populates="sessions")
    hall = relationship("Hall", back_populates="sessions")
    bookings = relationship("Booking", back_populates="session")

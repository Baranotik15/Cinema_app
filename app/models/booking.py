from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from app.enums import BookingStatus


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    seat_id = Column(Integer, ForeignKey("seats.id"), nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.pending, nullable=False)
    paid_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="bookings")
    session = relationship("Session", back_populates="bookings")
    seat = relationship("Seat", back_populates="bookings")

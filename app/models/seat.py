from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from app.enums import SeatType


class Seat(Base):
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, index=True)
    hall_id = Column(Integer, ForeignKey("halls.id"), nullable=False)
    row = Column(Integer, nullable=False)
    number = Column(Integer, nullable=False)
    seat_type = Column(Enum(SeatType, values_callable=lambda x: [e.value for e in x]), default=SeatType.standard, nullable=False)

    hall = relationship("Hall", back_populates="seats")
    bookings = relationship("Booking", back_populates="seat")

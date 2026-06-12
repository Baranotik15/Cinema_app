from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from app.enums import HallType


class Hall(Base):
    __tablename__ = "halls"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    capacity = Column(Integer, nullable=False)
    hall_type = Column(Enum(HallType, values_callable=lambda x: [e.value for e in x]), default=HallType.hall_2d, nullable=False)

    seats = relationship("Seat", back_populates="hall")
    sessions = relationship("Session", back_populates="hall")

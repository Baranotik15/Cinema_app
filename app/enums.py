from enum import Enum


class BookingStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"


class SessionStatus(str, Enum):
    scheduled = "scheduled"
    ongoing = "ongoing"
    finished = "finished"
    cancelled = "cancelled"


class SeatType(str, Enum):
    standard = "standard"
    vip = "vip"
    disabled = "disabled"


class HallType(str, Enum):
    hall_2d = "2D"
    hall_3d = "3D"
    imax = "IMAX"

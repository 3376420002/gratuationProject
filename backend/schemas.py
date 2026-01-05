from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class LoginRequest(BaseModel):
    username: str
    password: str

class RoomBase(BaseModel):
    number: str
    room_type: str
    price: float

class RoomCreate(RoomBase):
    pass

class RoomUpdate(RoomBase):
    pass

class RoomStatusUpdate(BaseModel):
    status: str
    guest_name: Optional[str] = None
    guest_id_card: Optional[str] = None
    guest_phone: Optional[str] = None

class Room(RoomBase):
    id: int
    status: str
    guest_name: Optional[str] = None
    class Config:
        from_attributes = True

class BookingCreate(BaseModel):
    guest_name: str
    room_id: int
    start_date: date
    end_date: date

class Booking(BookingCreate):
    id: int
    status: str
    class Config:
        from_attributes = True
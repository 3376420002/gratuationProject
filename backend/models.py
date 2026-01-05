from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)


class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, unique=True)
    room_type = Column(String)
    price = Column(Float)
    status = Column(String, default="空闲")
    guest_name = Column(String, nullable=True)
    guest_id_card = Column(String, nullable=True)
    guest_phone = Column(String, nullable=True)


    bookings = relationship("Booking", back_populates="room", cascade="all, delete-orphan")



class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    guest_name = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String, default="待入住")

    room = relationship("Room", back_populates="bookings")
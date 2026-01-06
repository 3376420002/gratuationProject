from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import date, datetime


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
    configuration = Column(Text, nullable=True)
    price = Column(Float)
    status = Column(String, default="空闲")  # 空闲、已入住、维修中

    # 维修增强字段
    fault_type = Column(String, nullable=True)  # 故障类型
    maintenance_detail = Column(String, nullable=True)
    is_insured = Column(Boolean, default=False)  # 是否报保险
    insurance_no = Column(String, nullable=True)  # 保险单号
    maintenance_cost = Column(Float, default=0.0)  # 维修成本

    guest_name = Column(String, nullable=True)
    guest_id_card = Column(String, nullable=True)
    guest_phone = Column(String, nullable=True)

    bookings = relationship("Booking", back_populates="room")
    comments = relationship("Comment", back_populates="room")


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    guest_name = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String, default="待入住")
    actual_revenue = Column(Float, default=0.0)  # 实际结账金额

    room = relationship("Room", back_populates="bookings")


# 1. 会员表
class Member(Base):
    __tablename__ = "members"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String, unique=True, index=True)
    password = Column(String)
    level = Column(String, default="普通会员")  # 普通, 白金, 钻石
    points = Column(Integer, default=0)
    balance = Column(Float, default=0.0)
    reg_date = Column(Date, default=date.today)
    logs = relationship("MemberLog", back_populates="member")

# 2. 积分与余额变动记录 (为以后做结算打基础)
class MemberLog(Base):
    __tablename__ = "member_logs"
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"))
    type = Column(String)  # "积分" 或 "余额"
    amount = Column(Float)
    reason = Column(String)
    create_time = Column(Date, default=date.today)
    member = relationship("Member", back_populates="logs")

# 3. 评价表 (关联房间)
class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    guest_name = Column(String)
    content = Column(Text)
    stars = Column(Integer)  # 1-5星
    create_time = Column(Date, default=date.today)
    room = relationship("Room", back_populates="comments")
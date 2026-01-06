from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


class RoomBase(BaseModel):
    number: str
    room_type: str
    price: float
    configuration: Optional[str] = None

class RoomCreate(RoomBase):
    pass

class RoomUpdate(RoomBase):
    fault_type: Optional[str] = None
    is_insured: Optional[bool] = False
    insurance_no: Optional[str] = None
    maintenance_cost: Optional[float] = 0.0
    maintenance_detail: Optional[str] = None

class RoomStatusUpdate(BaseModel):
    status: str
    guest_name: Optional[str] = None
    guest_id_card: Optional[str] = None
    guest_phone: Optional[str] = None
    # 扩展报修字段
    fault_type: Optional[str] = None
    is_insured: Optional[bool] = False
    insurance_no: Optional[str] = None


# ... 其他 LoginRequest, Booking 模型保持你原有的即可 ...
class LoginRequest(BaseModel):
    username: str
    password: str

class BookingCreate(BaseModel):
    guest_name: str
    room_id: int
    start_date: date
    end_date: date


class MemberBase(BaseModel):
    name: str
    phone: str
    level: str = "普通会员"
    points: int = 0
    balance: float = 0.0

class MemberCreate(MemberBase):
    password: str

class MemberUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    level: Optional[str] = None
    points: Optional[int] = None
    balance: Optional[float] = None

class Member(MemberBase):
    id: int
    reg_date: date

    class Config:
        from_attributes = True

# --- 评价相关 ---
class CommentBase(BaseModel):
    room_id: int
    guest_name: str
    content: str
    stars: int

class Comment(CommentBase):
    id: int
    create_time: date

    class Config:
        from_attributes = True


class MemberLog(BaseModel):
    id: int
    member_id: int
    type: str  # "积分" 或 "余额"
    amount: float
    reason: str
    create_time: date

    class Config:
        from_attributes = True

# --- 预订响应模型 (增强) ---
class BookingResponse(BaseModel):
    id: int
    room_id: int
    guest_name: str
    start_date: date
    end_date: date
    status: str
    actual_revenue: float # 对应 models.py 中的实际营收字段

    class Config:
        from_attributes = True
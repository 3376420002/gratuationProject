from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import date

import models, schemas, database
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="智慧酒店管理系统后端")

# 跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_token(token: str = Header(None)):
    if token != "fake-jwt-token":
        raise HTTPException(status_code=401, detail="未登录或登录已过期")
    return token


@app.post("/api/login")
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == request.username).first()
    if not user or user.password != request.password:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    return {"message": "登录成功", "token": "fake-jwt-token", "username": user.username}


@app.post("/api/init")
def init_data(db: Session = Depends(get_db)):
    if db.query(models.User).count() == 0:
        db.add(models.User(username="admin", password="123"))
    if db.query(models.Room).count() == 0:
        db.add(models.Room(number="101", room_type="标准间", price=199.0))
        db.add(models.Room(number="201", room_type="豪华大床房", price=399.0))
    db.commit()
    return {"msg": "初始化成功"}


@app.get("/api/rooms")
def read_rooms(db: Session = Depends(get_db)):
    return db.query(models.Room).all()


@app.post("/api/rooms")
def create_room(room: schemas.RoomCreate, db: Session = Depends(get_db)):
    db_room = db.query(models.Room).filter(models.Room.number == room.number).first()
    if db_room:
        raise HTTPException(status_code=400, detail="房间号已存在")
    new_room = models.Room(**room.dict())
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    return new_room


@app.delete("/api/rooms/{room_id}")
def delete_room(room_id: int, db: Session = Depends(get_db)):
    db_room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="房间未找到")
    db.delete(db_room)
    db.commit()
    return {"message": "房间删除成功"}


@app.put("/api/rooms/{room_id}/status")
def update_room_status(room_id: int, data: schemas.RoomStatusUpdate, db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")

    room.status = data.status
    room.guest_name = data.guest_name
    room.guest_id_card = data.guest_id_card
    room.guest_phone = data.guest_phone

    db.commit()
    return {"message": "更新成功"}

@app.get("/api/rooms/available")
def get_available_rooms(target_date: date, db: Session = Depends(get_db)):

    occupied_room_ids = db.query(models.Booking.room_id).filter(
        models.Booking.start_date <= target_date,
        models.Booking.end_date >= target_date,
        models.Booking.status != "已取消"
    ).all()

    occupied_ids = [r[0] for r in occupied_room_ids]

    available_rooms = db.query(models.Room).filter(~models.Room.id.in_(occupied_ids)).all()
    return available_rooms


@app.post("/api/bookings")
def create_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    conflict = db.query(models.Booking).filter(
        models.Booking.room_id == booking.room_id,
        models.Booking.status != "已取消",
        models.Booking.start_date < booking.end_date,
        models.Booking.end_date > booking.start_date
    ).first()

    if conflict:
        raise HTTPException(status_code=400, detail="该时间段房间已被占用")

    new_booking = models.Booking(
        room_id=booking.room_id,
        guest_name=booking.guest_name,
        start_date=booking.start_date,
        end_date=booking.end_date,
        status="待入住"
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return {"message": "预订成功", "id": new_booking.id}

@app.get("/api/bookings/today")
def get_today_bookings(db: Session = Depends(get_db)):
    from datetime import date
    today = date.today()


    bookings = db.query(models.Booking).filter(
        models.Booking.start_date == today,
        models.Booking.status == "待入住"
    ).all()

    result = []
    for b in bookings:
        room = db.query(models.Room).filter(models.Room.id == b.room_id).first()
        result.append({
            "guest_name": b.guest_name,
            "room_number": room.number if room else "未知",
            "time": "14:00 入住"
        })
    return result


@app.put("/api/rooms/{room_id}")
def update_room_info(room_id: int, room_data: schemas.RoomUpdate, db: Session = Depends(get_db)):
    db_room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="未找到该房间")

    db_room.room_type = room_data.room_type
    db_room.price = room_data.price

    db.commit()
    return {"message": "更新成功"}


from sqlalchemy import func

@app.get("/api/reports/stats")
def get_report_stats(db: Session = Depends(get_db)):
    from datetime import date
    today = date.today()

    today_revenue = db.query(func.sum(models.Room.price)).join(
        models.Booking, models.Room.id == models.Booking.room_id
    ).filter(
        models.Booking.start_date <= today,
        models.Booking.end_date >= today,
        models.Booking.status != "已取消"
    ).scalar() or 0

    total_rooms = db.query(models.Room).count()
    occupied_rooms = db.query(models.Room).filter(models.Room.status == "已入住").count()
    occupancy_rate = round((occupied_rooms / total_rooms * 100), 1) if total_rooms > 0 else 0

    pending_bookings = db.query(models.Booking).filter(
        models.Booking.status == "待入住",
        models.Booking.start_date >= today
    ).count()

    return [
        {"title": "今日预计营收", "value": str(today_revenue), "prefix": "¥"},
        {"title": "当前入住率", "value": str(occupancy_rate), "prefix": "%"},
        {"title": "待处理预订", "value": str(pending_bookings), "prefix": ""},
        {"title": "客房总数", "value": str(total_rooms), "prefix": ""}
    ]

@app.get("/api/reports/chart")
def get_chart_data(db: Session = Depends(get_db)):
    return {
        "days": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
        "data": [5, 8, 12, 7, 15, 20, 18] # 每日订单数
    }



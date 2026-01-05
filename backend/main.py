from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import date, datetime, timedelta
from sqlalchemy import func
import models, schemas, database
from database import engine, get_db
from fastapi.responses import StreamingResponse
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
import io
import pandas as pd

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
    today = date.today()

    # 1. 营收统计：基于房间单价和预订天数统计
    today_revenue = db.query(func.sum(models.Room.price)).join(
        models.Booking, models.Room.id == models.Booking.room_id
    ).filter(
        models.Booking.start_date <= today,
        models.Booking.end_date >= today,
        models.Booking.status != "已取消"
    ).scalar() or 0

    # 2. 入住率统计
    total_rooms = db.query(models.Room).count()
    occupied_rooms = db.query(models.Room).filter(models.Room.status == "已入住").count()
    occupancy_rate = round((occupied_rooms / total_rooms * 100), 1) if total_rooms > 0 else 0

    # 3. 待处理预订
    pending_bookings = db.query(models.Booking).filter(
        models.Booking.status == "待入住",
        models.Booking.start_date >= today
    ).count()

    return [
        {"title": "今日预计营收", "value": f"{today_revenue:.2f}", "prefix": "¥"},
        {"title": "当前入住率", "value": str(occupancy_rate), "prefix": "%"},
        {"title": "待处理预订", "value": str(pending_bookings), "prefix": ""},
        {"title": "客房总数", "value": str(total_rooms), "prefix": ""}
    ]


# --- 新增/优化：真实数据统计图表接口 ---
@app.get("/api/reports/chart")
def get_chart_data(db: Session = Depends(get_db)):
    days_labels = []
    counts_data = []

    # 循环过去 7 天
    for i in range(6, -1, -1):
        target_date = date.today() - timedelta(days=i)
        # 格式化日期作为坐标轴标签 (例如: 01-05)
        days_labels.append(target_date.strftime("%m-%d"))

        # 统计当天的订单数量
        count = db.query(models.Booking).filter(
            models.Booking.start_date == target_date,
            models.Booking.status != "已取消"
        ).count()
        counts_data.append(count)

    return {
        "days": days_labels,
        "data": counts_data
    }


@app.get("/api/reports/room-type-dist")
def get_room_type_distribution(db: Session = Depends(get_db)):
    # 统计不同房型的订单分布
    results = db.query(
        models.Room.room_type,
        func.count(models.Booking.id).label('count')
    ).join(models.Booking, models.Room.id == models.Booking.room_id).group_by(models.Room.room_type).all()

    return [{"name": r.room_type, "value": r.count} for r in results]


# --- 新增：实时房态墙数据 ---
@app.get("/api/reports/room-wall")
def get_room_wall(db: Session = Depends(get_db)):
    rooms = db.query(models.Room).all()
    # 返回精简的房态网格数据
    return [{
        "number": r.number,
        "type": r.room_type,
        "status": r.status,  # 已入住、空闲、维修等
        "price": r.price
    } for r in rooms]


from urllib.parse import quote
from datetime import datetime


@app.get("/api/reports/export-excel")
def export_excel(db: Session = Depends(get_db)):
    # 1. 获取当前系统日期
    today = date.today()

    # 2. 从数据库抓取原始数据
    bookings = db.query(
        models.Booking.id,
        models.Booking.guest_name,
        models.Room.number.label("room_number"),
        models.Booking.start_date,
        models.Booking.end_date,
        models.Booking.status
    ).join(models.Room, models.Room.id == models.Booking.room_id).all()

    # 3. 构造数据并同步更新数据库
    data = []
    for b in bookings:
        display_status = b.status

        # --- 核心逻辑：自动判定并同步数据库 ---
        if b.status == "待入住" and b.end_date < today:
            display_status = "已离店/完成"
            # 💡 这里直接更新数据库，确保前端页面也同步变掉
            db.query(models.Booking).filter(models.Booking.id == b.id).update({"status": "已离店/完成"})
        elif b.status == "待入住" and b.start_date <= today <= b.end_date:
            display_status = "入住中"
            db.query(models.Booking).filter(models.Booking.id == b.id).update({"status": "入住中"})

        data.append({
            "订单编号": b.id,
            "顾客姓名": b.guest_name,
            "房间号": b.room_number,
            "入住日期": b.start_date.strftime("%Y-%m-%d") if b.start_date else "",
            "离店日期": b.end_date.strftime("%Y-%m-%d") if b.end_date else "",
            "订单状态": display_status
        })

    # 提交数据库的所有更改
    db.commit()

    df = pd.DataFrame(data)

    # 4. 写入 Excel 并应用美化样式
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='营收报表')
        worksheet = writer.sheets['营收报表']

        # 蓝色表头样式
        header_fill = PatternFill(start_color="409EFF", end_color="409EFF", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        center_align = Alignment(horizontal="center", vertical="center")

        for i in range(1, len(df.columns) + 1):
            col_letter = get_column_letter(i)
            # 设置宽度为 25 像素，确保日期清晰
            worksheet.column_dimensions[col_letter].width = 25

            cell = worksheet.cell(row=1, column=i)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center_align

            # 给数据行也加上居中对齐，显得更整齐
            for row_idx in range(2, len(data) + 2):
                worksheet.cell(row=row_idx, column=i).alignment = center_align

    output.seek(0)

    # 5. 生成动态文件名下载
    timestamp = datetime.now().strftime('%H%M%S')
    filename = f"酒店营收分析_{timestamp}.xlsx"
    encoded_filename = quote(filename)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename*=utf-8''{encoded_filename}",
            "Cache-Control": "no-cache"
        }
    )
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import models
from database import engine, get_db
import httpx
from jose import jwt
from fastapi.middleware.cors import CORSMiddleware
import uuid 
import os

app = FastAPI(title="Booking Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

CATALOG_SERVICE_URL = "http://catalog_service:8001"
IDENTITY_SERVICE_URL = "http://identity_service:8003"
OTP_SERVICE_URL = "http://otp_service:8002"
PAYMENT_SERVICE_URL = "http://payment_service:8005"

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable is required")
ALGORITHM = "HS256"
security = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("id")
    except:
        raise HTTPException(status_code=401, detail="Invalid Token")

# --- Schemas ---
class ConcessionItemRequest(BaseModel):
    item_id: int
    quantity: int

class BookingRequest(BaseModel):
    showtime_id: int
    seat_ids: List[int]
    concessions: List[ConcessionItemRequest] = [] 

# --- API ---

@app.get("/bookings/mine")
def get_my_bookings(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    bookings = db.query(models.Booking)\
        .filter(models.Booking.user_id == user_id)\
        .order_by(models.Booking.booking_date.desc())\
        .all()
    
    results = []
    for b in bookings:
        tickets = db.query(models.Ticket).filter(models.Ticket.booking_id == b.booking_id).all()
        seat_ids = [t.seat_id for t in tickets]
        
        # Lấy seat labels từ catalog service
        seat_labels = []
        if seat_ids:
            try:
                with httpx.Client() as client:
                    res = client.post(f"{CATALOG_SERVICE_URL}/seats/batch", json={"seat_ids": seat_ids})
                    if res.status_code == 200:
                        seats_data = res.json()
                        # Sắp xếp theo row_code và seat_number
                        seats_data.sort(key=lambda x: (x["row_code"], x["seat_number"]))
                        seat_labels = [s["label"] for s in seats_data]
            except:
                seat_labels = [f"Seat {sid}" for sid in seat_ids]
        
        concessions = db.query(models.BookingConcession).filter(models.BookingConcession.booking_id == b.booking_id).all()
        
        results.append({
            "booking_id": b.booking_id,
            "showtime_id": b.showtime_id,
            "booking_date": b.booking_date.isoformat(),
            "total_amount": float(b.total_amount),
            "status": b.status,
            "payment_status": b.payment_status,
            "seats": seat_ids,
            "seat_labels": seat_labels,
            "concessions": [{"item_id": c.item_id, "quantity": c.quantity, "price": float(c.price)} for c in concessions],
            "tickets": [{"ticket_id": t.ticket_id, "qr_code": t.qr_code, "is_used": t.is_used} for t in tickets]
        })
        
    return results

@app.get("/bookings/showtime/{showtime_id}/booked-seats")
def get_booked_seats(showtime_id: int, db: Session = Depends(get_db)):
    booked = db.query(models.Ticket.seat_id).join(models.Booking).filter(
        models.Booking.showtime_id == showtime_id,
        models.Booking.status.in_(["PENDING", "CONFIRMED"])
    ).all()
    return [s[0] for s in booked]

@app.post("/bookings")
def create_booking(req: BookingRequest, 
                   user_id: int = Depends(get_current_user_id), 
                   db: Session = Depends(get_db)):
    
    # ===== VALIDATION 1: Không được đặt quá 8 ghế =====
    if len(req.seat_ids) > 8:
        raise HTTPException(status_code=400, detail="Không được đặt quá 8 ghế trong một lần!")
    
    # 1. Kiểm tra ghế đã đặt chưa
    existing_ticket = db.query(models.Ticket).join(models.Booking).filter(
        models.Booking.showtime_id == req.showtime_id,
        models.Ticket.seat_id.in_(req.seat_ids),
        models.Booking.status.in_(["PENDING", "CONFIRMED"])
    ).first()

    if existing_ticket:
        owner_booking = db.query(models.Booking).filter(
            models.Booking.booking_id == existing_ticket.booking_id
        ).first()

        if owner_booking and owner_booking.user_id == user_id and owner_booking.status == "PENDING":
            owner_booking.status = "CANCELLED"
            db.commit()
        else:
            raise HTTPException(status_code=400, detail=f"Ghế {existing_ticket.seat_id} đã có người đặt!")

    # ==================================================================
    # LOGIC TÍNH TIỀN TỪ CATALOG
    # ==================================================================
    BASE_PRICE = 50000.0
    
    try:
        st_res = httpx.get(f"{CATALOG_SERVICE_URL}/seat-types")
        seat_type_surcharges = {t['seat_type_id']: t['surcharge_rate'] for t in st_res.json()} if st_res.status_code == 200 else {}

        conc_res = httpx.get(f"{CATALOG_SERVICE_URL}/concessions")
        concession_prices = {c['item_id']: c['price'] for c in conc_res.json()} if conc_res.status_code == 200 else {}

        showtime_res = httpx.get(f"{CATALOG_SERVICE_URL}/showtimes/{req.showtime_id}")
        showtime_data = showtime_res.json()
        screen_id = showtime_data['screen_id']
        screen_type_surcharge = showtime_data.get('screen_type_surcharge', 0)
        
        seats_res = httpx.get(f"{CATALOG_SERVICE_URL}/screens/{screen_id}/seats")
        all_seats = seats_res.json() if seats_res.status_code == 200 else []
        screen_seats_map = {s['seat_id']: s for s in all_seats}

    except Exception as e:
        print(f"Error fetching catalog data: {e}")
        raise HTTPException(status_code=500, detail="Lỗi hệ thống: Không thể lấy dữ liệu giá vé.")

    # ===== VALIDATION 2: Kiểm tra tất cả ghế phải cùng loại =====
    selected_seats_info = [screen_seats_map.get(sid) for sid in req.seat_ids if screen_seats_map.get(sid)]
    if len(selected_seats_info) != len(req.seat_ids):
        raise HTTPException(status_code=400, detail="Một số ghế không tồn tại!")
    
    seat_types_selected = set(s['seat_type_id'] for s in selected_seats_info)
    if len(seat_types_selected) > 1:
        raise HTTPException(status_code=400, detail="Không được đặt mix nhiều loại ghế! Vui lòng chọn tất cả ghế cùng loại (Standard/VIP/Couple).")

    # ===== VALIDATION 3: Kiểm tra không để trống 1 ghế giữa =====
    # Nhóm ghế theo hàng
    rows_map = {}
    for s in selected_seats_info:
        row = s['row_code']
        if row not in rows_map:
            rows_map[row] = []
        rows_map[row].append(s['seat_number'])
    
    # Lấy tất cả ghế đã đặt trong suất chiếu này
    booked_seats = db.query(models.Ticket.seat_id).join(models.Booking).filter(
        models.Booking.showtime_id == req.showtime_id,
        models.Booking.status.in_(["PENDING", "CONFIRMED"])
    ).all()
    booked_seat_ids = [b[0] for b in booked_seats]
    
    # Kiểm tra từng hàng
    for row, selected_numbers in rows_map.items():
        # Lấy tất cả ghế trong hàng này
        row_seats = [s for s in all_seats if s['row_code'] == row and s['is_active']]
        row_seats.sort(key=lambda x: x['seat_number'])
        
        # Tạo map trạng thái ghế trong hàng
        seat_status = {}  # seat_number -> 'selected' | 'booked' | 'empty'
        for s in row_seats:
            if s['seat_id'] in req.seat_ids:
                seat_status[s['seat_number']] = 'selected'
            elif s['seat_id'] in booked_seat_ids:
                seat_status[s['seat_number']] = 'booked'
            else:
                seat_status[s['seat_number']] = 'empty'
        
        seat_numbers = sorted(seat_status.keys())
        
        # Kiểm tra có để trống 1 ghế đơn lẻ không
        for i, num in enumerate(seat_numbers):
            if seat_status[num] == 'empty':
                # Kiểm tra ghế bên trái và bên phải
                left_status = seat_status.get(num - 1) if num - 1 in seat_status else 'wall'
                right_status = seat_status.get(num + 1) if num + 1 in seat_status else 'wall'
                
                # Nếu ghế trống bị kẹp giữa 2 ghế đã chọn/đã đặt -> lỗi
                left_blocked = left_status in ['selected', 'booked', 'wall']
                right_blocked = right_status in ['selected', 'booked', 'wall']
                
                if left_blocked and right_blocked:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Không được để trống 1 ghế đơn lẻ! Ghế {row}{num} sẽ bị cô lập. Vui lòng chọn lại."
                    )

    # 2. Tính tiền ghế (bao gồm phụ thu loại màn hình)
    seat_total = 0.0
    tickets_to_create = []

    for seat_id in req.seat_ids:
        seat_info = screen_seats_map.get(seat_id, {})
        type_id = seat_info.get('seat_type_id', 1)
        surcharge = seat_type_surcharges.get(type_id, 0.0)
        real_price = BASE_PRICE + surcharge + screen_type_surcharge
        seat_total += real_price
        
        tickets_to_create.append({"seat_id": seat_id, "price": real_price})

    # 3. Tính tiền bắp nước
    concession_total = 0.0
    concessions_to_create = []

    for item in req.concessions:
        if item.quantity > 0:
            price = concession_prices.get(item.item_id, 0.0)
            concession_total += price * item.quantity
            
            concessions_to_create.append({
                "item_id": item.item_id,
                "quantity": item.quantity,
                "price": price
            })

    final_total = seat_total + concession_total

    # 4. Tạo Booking mới
    new_booking = models.Booking(
        user_id=user_id,
        showtime_id=req.showtime_id,
        total_amount=final_total,
        status="PENDING",
        payment_status="UNPAID"
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    # 5. Lưu vé chi tiết và TẠO MÃ QR UUID
    for t_data in tickets_to_create:
        generated_qr = str(uuid.uuid4()) 

        ticket = models.Ticket(
            booking_id=new_booking.booking_id, 
            seat_id=t_data['seat_id'], 
            price=t_data['price'],
            qr_code=generated_qr,
            is_used=False
        )
        db.add(ticket)

    # 6. Lưu bắp nước
    for c_data in concessions_to_create:
        conc = models.BookingConcession(
            booking_id=new_booking.booking_id,
            item_id=c_data['item_id'],
            quantity=c_data['quantity'],
            price=c_data['price']
        )
        db.add(conc)
    
    db.commit()

    return {
        "booking_id": new_booking.booking_id, 
        "total_amount": final_total,
        "status": "PENDING", 
        "message": "Booking created"
    }

@app.get("/bookings/{booking_id}")
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.booking_id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@app.put("/bookings/{booking_id}/cancel")
def cancel_booking_manual(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.booking_id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.status == "PENDING":
        booking.status = "CANCELLED"
        db.commit()
        return {"status": "CANCELLED", "message": "Đã hủy đơn hàng (chưa thanh toán)"}

    elif booking.status == "CONFIRMED":
        try:
            refund_payload = {
                "booking_id": booking.booking_id,
                "amount": float(booking.total_amount),
                "reason": "Khách hàng yêu cầu hủy"
            }
            res = httpx.post(f"{PAYMENT_SERVICE_URL}/refund", json=refund_payload, timeout=10.0)
            
            if res.status_code == 200:
                booking.status = "CANCELLED"
                booking.payment_status = "REFUNDED"
                db.commit()
                return {"status": "REFUNDED", "message": "Đã hủy vé và hoàn tiền thành công"}
            else:
                raise HTTPException(status_code=500, detail="Lỗi xử lý hoàn tiền")
                
        except Exception as e:
            print(f"Refund error: {e}")
            raise HTTPException(status_code=500, detail="Không thể kết nối Payment Service")

    else:
        raise HTTPException(status_code=400, detail="Không thể hủy đơn hàng này (Đã hủy rồi)")

@app.put("/bookings/{booking_id}/confirm")
def confirm_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.booking_id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking.status = "CONFIRMED"
    booking.payment_status = "PAID"
    db.commit()

    try:
        user_res = httpx.get(f"{IDENTITY_SERVICE_URL}/users/{booking.user_id}")
        user_email = user_res.json().get("email") if user_res.status_code == 200 else "unknown@mail.com"

        tickets = db.query(models.Ticket).filter(models.Ticket.booking_id == booking_id).all()
        
        # Lấy thông tin chi tiết từ showtime
        cinema_name = "CineWorld"
        screen_name = "Screen 1"
        movie_title = "Movie"
        start_time_str = str(booking.booking_date)
        
        seat_list = []
        try:
            showtime_res = httpx.get(f"{CATALOG_SERVICE_URL}/showtimes/{booking.showtime_id}")
            if showtime_res.status_code == 200:
                showtime_data = showtime_res.json()
                screen_id = showtime_data.get('screen_id')
                movie_title = showtime_data.get('movie_title', 'Movie')
                cinema_name = showtime_data.get('cinema_name', 'CineWorld')
                screen_name = showtime_data.get('screen_name', 'Screen 1')
                start_time_str = showtime_data.get('start_time', str(booking.booking_date))
                
                seats_res = httpx.get(f"{CATALOG_SERVICE_URL}/screens/{screen_id}/seats")
                if seats_res.status_code == 200:
                    seat_map = {s['seat_id']: f"{s['row_code']}{s['seat_number']}" for s in seats_res.json()}
                    for t in tickets:
                        seat_name = seat_map.get(t.seat_id, f"Ghế-{t.seat_id}") 
                        seat_list.append(seat_name)
                else:
                     seat_list = [f"Ghế-{t.seat_id}" for t in tickets]
            else:
                seat_list = [f"Ghế-{t.seat_id}" for t in tickets]
        except Exception as e:
            print(f"Error fetching seat names: {e}")
            seat_list = [f"Ghế-{t.seat_id}" for t in tickets]

        qr_code_sample = tickets[0].qr_code if tickets else "NO-QR"
        ticket_code = f"CW{booking.booking_id:06d}"

        concessions = db.query(models.BookingConcession).filter(models.BookingConcession.booking_id == booking_id).all()
        snack_str = "Không có"
        
        if concessions:
            items_str_list = []
            try:
                conc_res = httpx.get(f"{CATALOG_SERVICE_URL}/concessions")
                name_map = {c['item_id']: c['name'] for c in conc_res.json()} if conc_res.status_code == 200 else {}
                
                for c in concessions:
                    name = name_map.get(c.item_id, f"Item-{c.item_id}")
                    items_str_list.append(f"{name} (x{c.quantity})")
                
                snack_str = ", ".join(items_str_list)
            except:
                snack_str = ", ".join([f"Item-{c.item_id} (x{c.quantity})" for c in concessions])

        payload = {
            "email": user_email,
            "booking_id": booking.booking_id,
            "ticket_code": ticket_code,
            "movie_title": movie_title, 
            "cinema_name": cinema_name,
            "screen_name": screen_name,
            "start_time": start_time_str,
            "seats": seat_list,
            "concessions_text": snack_str,
            "amount": float(booking.total_amount),
            "qr_code": qr_code_sample 
        }
        httpx.post(f"{PAYMENT_SERVICE_URL}/send-ticket", json=payload, timeout=5.0)

    except Exception as e:
        print(f"Error sending ticket: {e}")

    return {"status": "updated"}

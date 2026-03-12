from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel
import models
from database import engine, get_db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Redemption Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

@app.get("/validate/{booking_id}")
def validate_ticket(booking_id: int, db: Session = Depends(get_db)):
    """Kiểm tra vé và lấy thông tin in"""
    
    booking = db.query(models.Booking)\
        .options(
            joinedload(models.Booking.showtime).joinedload(models.Showtime.movie),
            joinedload(models.Booking.showtime).joinedload(models.Showtime.screen).joinedload(models.Screen.cinema),
            joinedload(models.Booking.tickets).joinedload(models.Ticket.seat)
        )\
        .filter(models.Booking.booking_id == booking_id).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Vé không tồn tại")
    
    if booking.payment_status != "PAID":
        return {"status": "INVALID", "message": "Vé chưa thanh toán!"}
    
    used_tickets = [t for t in booking.tickets if t.is_used]
    status = "USED" if used_tickets else "VALID"
    message = "CẢNH BÁO: Vé đã dùng!" if used_tickets else "Vé hợp lệ. Mời vào rạp."

    seats = [f"{t.seat.row_code}{t.seat.seat_number}" for t in booking.tickets]
    
    ticket_data = {
        "booking_id": booking.booking_id,
        "movie": booking.showtime.movie.title,
        "cinema": booking.showtime.screen.cinema.name,
        "screen": booking.showtime.screen.name,
        "time": booking.showtime.start_time.strftime("%H:%M %d/%m/%Y"),
        "seats": ", ".join(seats),
        "price": booking.total_amount
    }

    return {
        "status": status, 
        "message": message,
        "ticket_data": ticket_data
    }

@app.post("/checkin/{booking_id}")
def checkin_ticket(booking_id: int, db: Session = Depends(get_db)):
    tickets = db.query(models.Ticket).filter(models.Ticket.booking_id == booking_id).all()
    if not tickets:
        raise HTTPException(status_code=404, detail="Not found")
        
    for t in tickets:
        t.is_used = True
    
    db.commit()
    return {"status": "SUCCESS", "message": "Check-in thành công!"}
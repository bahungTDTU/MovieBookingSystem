from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import httpx
import datetime
import uuid
import models
from database import engine, get_db
from fastapi.middleware.cors import CORSMiddleware
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage 
import io
import barcode
from barcode.writer import ImageWriter

app = FastAPI(title="Payment Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

BOOKING_SERVICE_URL = "http://booking_service:8004"

# Cấu hình SMTP 
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "bahungacezero@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "blvu uwqz awip nton")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

def generate_barcode_bytes(text: str):
    """Tạo barcode dạng bytes (PNG)"""
    try:
        Code128 = barcode.get_barcode_class('code128')
        rv = io.BytesIO()
        code_obj = Code128(str(text), writer=ImageWriter())
        code_obj.write(rv, options={"write_text": False}) 
        return rv.getvalue()
    except Exception as e:
        print(f"Barcode Error: {e}")
        return None

def send_email_via_smtp(to_email: str, subject: str, html_body: str, barcode_data=None):
    """Gửi email qua SMTP Gmail"""
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        print("⚠️ SMTP config missing.")
        return False
    try:
        msg = MIMEMultipart('related')
        msg['From'] = SMTP_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject

        msg_alternative = MIMEMultipart('alternative')
        msg.attach(msg_alternative)
        msg_alternative.attach(MIMEText(html_body, 'html'))

        if barcode_data:
            img = MIMEImage(barcode_data)
            img.add_header('Content-ID', '<barcode_image>')
            img.add_header('Content-Disposition', 'inline', filename='barcode.png')
            msg.attach(img)

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

# --- SCHEMAS ---
class PaymentRequest(BaseModel):
    booking_id: int
    amount: float
    payment_method: str = "MOMO"

class MockPaymentRequest(BaseModel):
    booking_id: int
    amount: float
    card_number: str = "4111111111111111"
    card_holder: str = "TEST USER"
    expiry: str = "12/25"
    cvv: str = "123"

class RefundRequest(BaseModel):
    booking_id: int
    amount: float
    reason: str = "N/A"

class TicketEmailRequest(BaseModel):
    email: str
    booking_id: int
    ticket_code: str
    movie_title: str
    cinema_name: str
    screen_name: str
    start_time: str
    seats: list
    concessions_text: str = "Không có"
    amount: float
    qr_code: str 

# --- API ---

@app.get("/")
def health_check():
    return {"status": "Payment Service is running"}

@app.post("/pay")
def process_payment(req: PaymentRequest, db: Session = Depends(get_db)):
    gateway_ref = f"{req.payment_method}_{uuid.uuid4().hex[:8].upper()}"
    
    new_trans = models.Transaction(
        booking_id=req.booking_id,
        amount=req.amount,
        transaction_type="PAYMENT",
        status="PENDING",
        payment_method=req.payment_method,
        gateway_ref_id=gateway_ref,
        created_at=datetime.datetime.utcnow()
    )
    db.add(new_trans)
    db.commit()
    db.refresh(new_trans)

    if req.payment_method == "FAILURE_DEMO":
        new_trans.status = "FAILED"
        db.commit()
        raise HTTPException(status_code=400, detail="Giao dịch bị từ chối (Demo Lỗi).")

    new_trans.status = "SUCCESS"
    db.commit()

    try:
        confirm_url = f"{BOOKING_SERVICE_URL}/bookings/{req.booking_id}/confirm"
        response = httpx.put(confirm_url, timeout=10.0)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Lỗi confirm booking")
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Không kết nối được Booking Service")

    return {
        "status": "SUCCESS",
        "message": "Thanh toán thành công",
        "transaction_id": new_trans.transaction_id
    }

@app.post("/mock-payment")
def process_mock_payment(req: MockPaymentRequest, db: Session = Depends(get_db)):
    """Mock Payment - Giả lập thanh toán thẻ"""
    # Validate card number (mock validation)
    if not req.card_number or len(req.card_number) < 13:
        raise HTTPException(status_code=400, detail="Số thẻ không hợp lệ")
    
    if not req.cvv or len(req.cvv) < 3:
        raise HTTPException(status_code=400, detail="CVV không hợp lệ")
    
    # Simulate payment processing
    gateway_ref = f"MOCK_{uuid.uuid4().hex[:8].upper()}"
    
    new_trans = models.Transaction(
        booking_id=req.booking_id,
        amount=req.amount,
        transaction_type="PAYMENT",
        status="PENDING",
        payment_method="MOCK_CARD",
        gateway_ref_id=gateway_ref,
        created_at=datetime.datetime.utcnow()
    )
    db.add(new_trans)
    db.commit()
    db.refresh(new_trans)
    
    # Mock: Card ending with 0000 will fail
    if req.card_number.endswith("0000"):
        new_trans.status = "FAILED"
        db.commit()
        raise HTTPException(status_code=400, detail="Thẻ bị từ chối! Vui lòng thử thẻ khác.")
    
    new_trans.status = "SUCCESS"
    db.commit()
    
    # Confirm booking
    try:
        confirm_url = f"{BOOKING_SERVICE_URL}/bookings/{req.booking_id}/confirm"
        response = httpx.put(confirm_url, timeout=10.0)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Lỗi confirm booking")
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Không kết nối được Booking Service")
    
    return {
        "status": "SUCCESS",
        "message": "Thanh toán Mock thành công!",
        "transaction_id": new_trans.transaction_id,
        "card_last4": req.card_number[-4:]
    }

@app.post("/refund")
def process_refund(req: RefundRequest, db: Session = Depends(get_db)):
    refund_trans = models.Transaction(
        booking_id=req.booking_id,
        amount=req.amount,
        transaction_type="REFUND",
        status="SUCCESS",
        payment_method="SYSTEM",
        gateway_ref_id=f"REFUND_{uuid.uuid4().hex[:8].upper()}",
        created_at=datetime.datetime.utcnow()
    )
    db.add(refund_trans)
    db.commit()
    
    return {
        "status": "REFUNDED",
        "message": f"Đã hoàn tiền {req.amount} cho đơn #{req.booking_id}",
        "transaction_id": refund_trans.transaction_id
    }

@app.get("/transactions/{booking_id}")
def get_history(booking_id: int, db: Session = Depends(get_db)):
    trans = db.query(models.Transaction).filter(models.Transaction.booking_id == booking_id).all()
    return trans

@app.post("/send-ticket")
def send_ticket_email(req: TicketEmailRequest):
    barcode_bytes = generate_barcode_bytes(str(req.booking_id))
    
    seats_html = ", ".join([f"<b>{s}</b>" for s in req.seats])
    
    body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #ddd;">
        <div style="background-color: #e50914; color: white; padding: 15px; text-align: center;">
            <h2>VÉ ĐIỆN TỬ / E-TICKET</h2>
        </div>
        <div style="padding: 20px;">
            <p>Cảm ơn bạn đã đặt vé tại CineWorld.</p>
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee; width: 35%;">Mã vé:</td><td style="font-weight:bold; color: #e50914;">{req.ticket_code}</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee;">Phim:</td><td><b>{req.movie_title}</b></td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee;">Rạp:</td><td><b>{req.cinema_name}</b></td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee;">Phòng chiếu:</td><td><b>{req.screen_name}</b></td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee;">Suất chiếu:</td><td>{req.start_time}</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee;">Ghế:</td><td>{seats_html}</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee;">Bắp nước:</td><td>{req.concessions_text}</td></tr>
                <tr><td style="padding: 8px; border-bottom: 2px solid #e50914;">Tổng tiền:</td><td style="color: #e50914; font-weight: bold; font-size: 18px;">{req.amount:,.0f} VND</td></tr>
            </table>

            <div style="text-align: center; margin-top: 30px; background: #f9f9f9; padding: 20px; border-radius: 8px;">
                <p style="margin-bottom: 5px; font-weight:bold;">Mã Check-in (QR):</p>
                <div style="font-size: 18px; font-weight: bold; margin-bottom: 15px; color: #333; background: #fff; padding: 10px; border-radius: 5px; border: 2px dashed #e50914;">{req.qr_code}</div>
                <p style="margin-bottom: 5px;">Mã Barcode:</p>
                <img src="cid:barcode_image" alt="Booking Barcode" style="max-width: 300px; height: auto;" />
                <p style="color: #777; font-size: 12px; margin-top: 10px;">Booking ID: #{req.booking_id}</p>
            </div>
            
            <div style="margin-top: 20px; padding: 15px; background: #fff3cd; border-radius: 5px; font-size: 13px; color: #856404;">
                <b>Lưu ý:</b> Vui lòng đến rạp trước giờ chiếu 15-30 phút. Xuất trình mã QR/Barcode tại quầy để nhận vé.
            </div>
        </div>
        <div style="background: #333; color: #999; padding: 15px; text-align: center; font-size: 12px;">
            CineWorld - Hệ thống đặt vé xem phim trực tuyến<br>
            Hotline: 1900 xxxx | Email: support@cineworld.vn
        </div>
    </div>
    """
    
    if send_email_via_smtp(req.email, f"🎬 Vé xem phim #{req.booking_id} - {req.movie_title}", body, barcode_bytes):
        return {"status": "sent", "message": "Email vé đã được gửi"}
    else:
        raise HTTPException(status_code=500, detail="Lỗi gửi email")
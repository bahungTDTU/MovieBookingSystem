from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
import models
from database import engine, get_db
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI(title="OTP Service")

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

def send_email_via_smtp(to_email: str, subject: str, html_body: str):
    """
    Gửi email đơn giản (chỉ text/html, không cần barcode/ảnh).
    Dùng riêng cho việc gửi mã OTP.
    """
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        print("⚠️ SMTP config missing.")
        return False
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = SMTP_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(html_body, 'html'))

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

# --- SCHEMAS ---
class OTPRequest(BaseModel):
    identifier: str

class OTPValidate(BaseModel):
    identifier: str
    otp_code: str

# --- API ENDPOINTS ---

@app.post("/generate")
def generate_otp(req: OTPRequest, db: Session = Depends(get_db)):
    db.query(models.OTP).filter(models.OTP.identifier == req.identifier).delete()
    db.commit()

    code = str(random.randint(100000, 999999))
    
    db_otp = models.OTP(
        identifier=req.identifier, 
        otp_code=code, 
        expires_at=datetime.now() + timedelta(minutes=5)
    )
    db.add(db_otp)
    db.commit()
    
    body = f"""
    <div style="font-family: Arial; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
        <h2 style="color: #e50914;">Mã xác thực CineWorld</h2>
        <p>Mã OTP mới của bạn là:</p>
        <h1 style="background:#f4f4f4; padding:10px; text-align:center; letter-spacing: 5px; color:#333;">{code}</h1>
        <p style="color:#666; font-size:12px;">Mã này sẽ hết hạn sau 5 phút. Các mã cũ đã bị vô hiệu hóa.</p>
    </div>
    """
    
    send_email_via_smtp(req.identifier, "Mã OTP Mới", body)
    
    return {"status": "success", "message": "New OTP sent"}

@app.post("/validate")
def validate_otp(req: OTPValidate, db: Session = Depends(get_db)):
    otp_record = db.query(models.OTP).filter(
        models.OTP.identifier == req.identifier,
        models.OTP.otp_code == req.otp_code,
        models.OTP.expires_at > datetime.now()
    ).first()
    
    if not otp_record:
        raise HTTPException(status_code=400, detail="Mã OTP không hợp lệ hoặc đã hết hạn")
    
    db.delete(otp_record)
    db.commit()
    
    return {"status": "valid"}

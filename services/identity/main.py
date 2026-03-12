from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models, utils
from database import engine, get_db
import httpx
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Identity Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

OTP_SERVICE_URL = "http://otp_service:8002"

# --- SCHEMAS ---
class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str

class VerifyAccount(BaseModel):
    email: str
    otp_code: str

class UserLogin(BaseModel):
    email: str
    password: str

class ResendOTPRequest(BaseModel):
    email: str
    
class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    otp_code: str
    new_password: str

# --- API ENDPOINTS ---

@app.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email đã tồn tại")
    
    new_user = models.User(
        email=user.email,
        full_name=user.full_name,
        password_hash=utils.get_password_hash(user.password),
        is_verified=False
    )
    db.add(new_user)
    db.commit()
    
    # Gọi OTP Service
    try:
        httpx.post(f"{OTP_SERVICE_URL}/generate", json={"identifier": user.email}, timeout=5.0)
    except:
        pass 
        
    return {"message": "Đăng ký thành công. Vui lòng kiểm tra email."}

@app.post("/resend-otp")
def resend_otp(req: ResendOTPRequest, db: Session = Depends(get_db)):
    """Gửi lại mã OTP cho tài khoản chưa kích hoạt"""
    user = db.query(models.User).filter(models.User.email == req.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Email không tồn tại")
    
    if user.is_verified:
        raise HTTPException(status_code=400, detail="Tài khoản này đã kích hoạt rồi.")

    try:
        httpx.post(f"{OTP_SERVICE_URL}/generate", json={"identifier": req.email}, timeout=5.0)
    except:
        raise HTTPException(status_code=500, detail="Lỗi kết nối OTP Service")
        
    return {"message": "Đã gửi lại mã OTP mới"}

@app.post("/verify")
def verify_account(req: VerifyAccount, db: Session = Depends(get_db)):
    # 1. Validate OTP
    try:
        response = httpx.post(f"{OTP_SERVICE_URL}/validate", json={"identifier": req.email, "otp_code": req.otp_code})
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Mã OTP không đúng hoặc đã hết hạn")
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=500, detail="Lỗi kết nối OTP Service")

    # 2. Update User
    user = db.query(models.User).filter(models.User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.is_verified = True
    db.commit()
    return {"message": "Xác thực thành công! Hãy đăng nhập."}

@app.post("/login")
def login(req: UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == req.email).first()
    
    if not user or not utils.verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Sai email hoặc mật khẩu")
    

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Tài khoản chưa kích hoạt")
        
    token = utils.create_access_token({"sub": user.email, "id": user.user_id, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email không tồn tại")
    
    try:
        httpx.post(f"{OTP_SERVICE_URL}/generate", json={"identifier": req.email}, timeout=5.0)
    except:
        raise HTTPException(status_code=500, detail="Lỗi gửi OTP")
    return {"message": "OTP sent"}

@app.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        otp_res = httpx.post(f"{OTP_SERVICE_URL}/validate", json={
            "identifier": req.email, 
            "otp_code": req.otp_code
        }, timeout=5.0)
        if otp_res.status_code != 200:
            raise HTTPException(status_code=400, detail="OTP sai")
    except:
        raise HTTPException(status_code=400, detail="Lỗi xác thực OTP")

    user = db.query(models.User).filter(models.User.email == req.email).first()
    if not user: raise HTTPException(status_code=404, detail="User not found")
        
    user.password_hash = utils.get_password_hash(req.new_password)
    db.commit()
    return {"message": "Đổi mật khẩu thành công"}

@app.get("/users/{user_id}")
def get_user_info(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user.user_id, "email": user.email, "full_name": user.full_name}
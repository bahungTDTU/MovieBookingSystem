from sqlalchemy import Column, Integer, String, DateTime, Boolean, BigInteger
from database import Base

class OTP(Base):
    __tablename__ = "otps"
    
    otp_id = Column(BigInteger, primary_key=True, index=True)
    identifier = Column(String(100)) 
    otp_code = Column(String(10))
    expires_at = Column(DateTime)
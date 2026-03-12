from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True)
    full_name = Column(String(100))
    password_hash = Column(String(255))
    role = Column(String(20), default="MEMBER")
    is_verified = Column(Boolean, default=False)
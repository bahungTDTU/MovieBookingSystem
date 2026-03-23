from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from database import Base
import datetime

# 1. Bảng Đơn hàng
class Booking(Base):
    __tablename__ = "bookings"
    
    booking_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    showtime_id = Column(Integer, nullable=False)
    booking_date = Column(DateTime, default=datetime.datetime.utcnow)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(String(50), default="PENDING")
    payment_status = Column(String(50), default="UNPAID")
    
    # Quan hệ
    tickets = relationship("Ticket", back_populates="booking", cascade="all, delete-orphan")
    concessions = relationship("BookingConcession", back_populates="booking", cascade="all, delete-orphan")

# 2. Bảng Vé
class Ticket(Base):
    __tablename__ = "tickets"
    
    ticket_id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.booking_id"))
    seat_id = Column(Integer, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    qr_code = Column(String(255), nullable=True)
    is_used = Column(Boolean, default=False)
    
    booking = relationship("Booking", back_populates="tickets")

# 3. Bảng Bắp nước 
class BookingConcession(Base):
    __tablename__ = "booking_concessions"
    
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.booking_id"))
    item_id = Column(Integer, nullable=False)
    quantity = Column(Integer, default=1)
    price = Column(DECIMAL(10, 2), nullable=False)
    
    booking = relationship("Booking", back_populates="concessions")
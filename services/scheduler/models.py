from sqlalchemy import Column, Integer, String, DateTime
from database import Base
import datetime

class Booking(Base):
    __tablename__ = "bookings"
    
    booking_id = Column(Integer, primary_key=True, index=True)
    status = Column(String(50))
    booking_date = Column(DateTime)
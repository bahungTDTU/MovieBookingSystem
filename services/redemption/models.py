from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, DECIMAL
from sqlalchemy.orm import relationship
from database import Base

# --- CÁC BẢNG CATALOG  ---
class Cinema(Base):
    __tablename__ = "cinemas"
    cinema_id = Column(Integer, primary_key=True)
    name = Column(String(100))

class Screen(Base):
    __tablename__ = "screens"
    screen_id = Column(Integer, primary_key=True)
    cinema_id = Column(Integer, ForeignKey("cinemas.cinema_id"))
    name = Column(String(50))
    cinema = relationship("Cinema")

class Movie(Base):
    __tablename__ = "movies"
    movie_id = Column(Integer, primary_key=True)
    title = Column(String(255))

class Showtime(Base):
    __tablename__ = "showtimes"
    showtime_id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey("movies.movie_id"))
    screen_id = Column(Integer, ForeignKey("screens.screen_id"))
    start_time = Column(DateTime)
    
    movie = relationship("Movie")
    screen = relationship("Screen")

class Seat(Base):
    __tablename__ = "seats"
    seat_id = Column(Integer, primary_key=True)
    row_code = Column(String(5))
    seat_number = Column(Integer)

# --- CÁC BẢNG BOOKING ---
class Booking(Base):
    __tablename__ = "bookings"
    
    booking_id = Column(Integer, primary_key=True, index=True)
    showtime_id = Column(Integer, ForeignKey("showtimes.showtime_id"))
    status = Column(String(50))         
    payment_status = Column(String(50)) 
    booking_date = Column(DateTime)
    total_amount = Column(DECIMAL(10, 2))
    
    showtime = relationship("Showtime")
    tickets = relationship("Ticket", back_populates="booking")

class Ticket(Base):
    __tablename__ = "tickets"
    
    ticket_id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.booking_id"))
    seat_id = Column(Integer, ForeignKey("seats.seat_id"))
    price = Column(DECIMAL(10, 2))
    is_used = Column(Boolean, default=False)
    
    booking = relationship("Booking", back_populates="tickets")
    seat = relationship("Seat")
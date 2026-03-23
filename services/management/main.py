from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel
import models
from database import engine, get_db
from jose import jwt
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI(title="Management Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

# --- SECURITY ---
SECRET_KEY = "SECRET_KEY_SIEU_BAO_MAT_CUA_BAN"
ALGORITHM = "HS256"

security = HTTPBearer()

def check_admin_role(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency xác thực quyền Admin.
    Sử dụng HTTPBearer để hiện nút Authorize trên Swagger.
    """
    token = credentials.credentials
    try:
        # Giải mã Token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role = payload.get("role")
        
        # Kiểm tra quyền
        if role not in ["ADMIN", "MANAGER"]:
            raise HTTPException(status_code=403, detail="Không có quyền truy cập! Yêu cầu quyền ADMIN.")
            
        return payload
    except:
        raise HTTPException(status_code=401, detail="Token không hợp lệ hoặc đã hết hạn.")

# --- SCHEMAS ---
class MovieCreate(BaseModel):
    title: str
    duration_minutes: int
    status: str
    poster_url: str
    director: str = None
    actors: str = None
    genre: str = None
    release_date: str = None
    language: str = None
    age_rating: str = None
    description: str = None

class MovieStatusUpdate(BaseModel):
    status: str 

class CinemaCreate(BaseModel):
    name: str
    address: str

class ScreenCreate(BaseModel):
    cinema_id: int
    name: str
    total_seats: int = 50
    screen_type_id: int = 1
    rows_count: int = 5
    cols_count: int = 10

class ScreenTypeCreate(BaseModel):
    name: str
    surcharge: float = 0

class ShowtimeCreate(BaseModel):
    movie_id: int
    screen_id: int
    start_time: datetime 
    base_price: float

class ShowtimeBatchCreate(BaseModel):
    movie_id: int
    screen_ids: List[int]
    start_time: datetime 
    base_price: float

class SeatTypeCreate(BaseModel):
    name: str
    surcharge_rate: float

class SeatTypeUpdate(BaseModel):
    name: str = None
    surcharge_rate: float = None

class SeatBatchCreate(BaseModel):
    screen_id: int
    seat_type_id: int
    row_code: str
    start_number: int
    end_number: int

class SeatBatchUpdate(BaseModel):
    screen_id: int
    seat_type_id: int
    row_code: str
    start_number: int
    end_number: int
    is_active: bool

class SeatUpdate(BaseModel):
    seat_type_id: int = None
    is_active: bool = None
    
class ConcessionCreate(BaseModel):
    name: str
    price: float

# --- API ---

@app.get("/screens")
def get_all_screens(user=Depends(check_admin_role), db: Session = Depends(get_db)):
    screens = db.query(models.Screen).options(
        joinedload(models.Screen.cinema),
        joinedload(models.Screen.screen_type)
    ).all()
    results = []
    for s in screens:
        results.append({
            "screen_id": s.screen_id,
            "name": s.name,
            "cinema_name": s.cinema.name,
            "total_seats": s.total_seats,
            "screen_type_id": s.screen_type_id,
            "screen_type_name": s.screen_type.name if s.screen_type else "2D",
            "screen_type_surcharge": float(s.screen_type.surcharge) if s.screen_type else 0,
            "rows_count": s.rows_count,
            "cols_count": s.cols_count
        })
    return results

@app.get("/cinemas")
def get_all_cinemas(user=Depends(check_admin_role), db: Session = Depends(get_db)):
    return db.query(models.Cinema).all()

@app.post("/cinemas")
def add_cinema(c: CinemaCreate, user=Depends(check_admin_role), db: Session = Depends(get_db)):
    new_c = models.Cinema(name=c.name, address=c.address)
    db.add(new_c)
    db.commit()
    return {"status": "success", "message": f"Đã thêm rạp: {c.name}"}

@app.post("/screens")
def add_screen(s: ScreenCreate, user=Depends(check_admin_role), db: Session = Depends(get_db)):
    cinema = db.query(models.Cinema).filter(models.Cinema.cinema_id == s.cinema_id).first()
    if not cinema:
        raise HTTPException(status_code=404, detail="Rạp không tồn tại")
    new_s = models.Screen(
        cinema_id=s.cinema_id, 
        name=s.name, 
        total_seats=s.total_seats,
        screen_type_id=s.screen_type_id,
        rows_count=s.rows_count,
        cols_count=s.cols_count
    )
    db.add(new_s)
    db.commit()
    db.refresh(new_s)
    return {"status": "success", "message": f"Đã thêm phòng {s.name} vào rạp {cinema.name}", "screen_id": new_s.screen_id}

@app.post("/movies")
def add_movie(movie: MovieCreate, user=Depends(check_admin_role), db: Session = Depends(get_db)):
    movie_data = {
        "title": movie.title,
        "duration_minutes": movie.duration_minutes,
        "status": movie.status,
        "poster_url": movie.poster_url,
        "director": movie.director,
        "actors": movie.actors,
        "genre": movie.genre,
        "language": movie.language,
        "age_rating": movie.age_rating,
        "description": movie.description
    }
    if movie.release_date:
        from datetime import datetime as dt
        movie_data["release_date"] = dt.strptime(movie.release_date, "%Y-%m-%d").date()
    
    new_movie = models.Movie(**movie_data)
    db.add(new_movie)
    db.commit()
    return {"status": "success", "message": f"Đã thêm phim: {movie.title}"}

@app.put("/movies/{movie_id}/status")
def update_movie_status(movie_id: int, status_update: MovieStatusUpdate, user=Depends(check_admin_role), db: Session = Depends(get_db)):
    movie = db.query(models.Movie).filter(models.Movie.movie_id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    movie.status = status_update.status
    db.commit()
    return {"status": "success", "message": f"Đã cập nhật trạng thái thành {status_update.status}"}

@app.post("/showtimes")
def add_showtime(st: ShowtimeCreate, user=Depends(check_admin_role), db: Session = Depends(get_db)):
    # Kiểm tra xung đột lịch chiếu (không cho add cùng giờ trong cùng phòng)
    movie = db.query(models.Movie).filter(models.Movie.movie_id == st.movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Phim không tồn tại")
    
    movie_duration = movie.duration_minutes
    new_start = st.start_time
    new_end = new_start + timedelta(minutes=movie_duration + 15)  # +15 phút dọn dẹp
    
    # Tìm các suất chiếu đã có trong phòng này
    existing_showtimes = db.query(models.Showtime).filter(
        models.Showtime.screen_id == st.screen_id
    ).all()
    
    for existing in existing_showtimes:
        existing_movie = db.query(models.Movie).filter(models.Movie.movie_id == existing.movie_id).first()
        existing_duration = existing_movie.duration_minutes if existing_movie else 120
        existing_end = existing.start_time + timedelta(minutes=existing_duration + 15)
        
        # Kiểm tra xung đột: suất mới không được nằm trong khoảng thời gian của suất cũ
        if not (new_end <= existing.start_time or new_start >= existing_end):
            raise HTTPException(
                status_code=400, 
                detail=f"Xung đột lịch chiếu! Phòng này đã có suất chiếu từ {existing.start_time.strftime('%H:%M %d/%m')} đến {existing_end.strftime('%H:%M')}"
            )
    
    new_st = models.Showtime(**st.dict())
    db.add(new_st)
    db.commit()
    return {"status": "success", "message": "Đã lên lịch chiếu thành công"}

@app.post("/showtimes/batch")
def add_showtime_batch(st: ShowtimeBatchCreate, user=Depends(check_admin_role), db: Session = Depends(get_db)):
    movie = db.query(models.Movie).filter(models.Movie.movie_id == st.movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Phim không tồn tại")
    
    movie_duration = movie.duration_minutes
    new_start = st.start_time
    new_end = new_start + timedelta(minutes=movie_duration + 15)
    
    conflicts = []
    success_count = 0
    
    for screen_id in st.screen_ids:
        # Kiểm tra xung đột cho từng phòng
        existing_showtimes = db.query(models.Showtime).filter(
            models.Showtime.screen_id == screen_id
        ).all()
        
        has_conflict = False
        for existing in existing_showtimes:
            existing_movie = db.query(models.Movie).filter(models.Movie.movie_id == existing.movie_id).first()
            existing_duration = existing_movie.duration_minutes if existing_movie else 120
            existing_end = existing.start_time + timedelta(minutes=existing_duration + 15)
            
            if not (new_end <= existing.start_time or new_start >= existing_end):
                screen = db.query(models.Screen).filter(models.Screen.screen_id == screen_id).first()
                conflicts.append(f"Phòng {screen.name if screen else screen_id}")
                has_conflict = True
                break
        
        if not has_conflict:
            new_st = models.Showtime(
                movie_id=st.movie_id,
                screen_id=screen_id,
                start_time=st.start_time,
                base_price=st.base_price
            )
            db.add(new_st)
            success_count += 1
    
    db.commit()
    
    message = f"Đã tạo {success_count} suất chiếu"
    if conflicts:
        message += f". Bỏ qua {len(conflicts)} phòng do xung đột: {', '.join(conflicts)}"
    
    return {"status": "success", "message": message, "created": success_count, "conflicts": conflicts}

# --- API GHẾ ---
@app.get("/seat-types")
def get_seat_types(user=Depends(check_admin_role), db: Session = Depends(get_db)):
    return db.query(models.SeatType).all()

@app.post("/seat-types")
def add_seat_type(st: SeatTypeCreate, user=Depends(check_admin_role), db: Session = Depends(get_db)):
    new_st = models.SeatType(name=st.name, surcharge_rate=st.surcharge_rate)
    db.add(new_st)
    db.commit()
    return {"status": "success", "message": f"Đã thêm loại ghế: {st.name}"}

@app.put("/seat-types/{seat_type_id}")
def update_seat_type(seat_type_id: int, st: SeatTypeUpdate, user=Depends(check_admin_role), db: Session = Depends(get_db)):
    """Cập nhật loại ghế và giá tiền"""
    seat_type = db.query(models.SeatType).filter(models.SeatType.seat_type_id == seat_type_id).first()
    if not seat_type:
        raise HTTPException(status_code=404, detail="Loại ghế không tồn tại")
    
    if st.name is not None:
        seat_type.name = st.name
    if st.surcharge_rate is not None:
        seat_type.surcharge_rate = st.surcharge_rate
    
    db.commit()
    return {"status": "success", "message": f"Đã cập nhật loại ghế: {seat_type.name}"}

@app.delete("/seat-types/{seat_type_id}")
def delete_seat_type(seat_type_id: int, user=Depends(check_admin_role), db: Session = Depends(get_db)):
    """Xóa loại ghế"""
    seat_type = db.query(models.SeatType).filter(models.SeatType.seat_type_id == seat_type_id).first()
    if not seat_type:
        raise HTTPException(status_code=404, detail="Loại ghế không tồn tại")
    
    # Kiểm tra xem có ghế nào đang sử dụng loại này không
    seats_using = db.query(models.Seat).filter(models.Seat.seat_type_id == seat_type_id).count()
    if seats_using > 0:
        raise HTTPException(status_code=400, detail=f"Không thể xóa! Có {seats_using} ghế đang sử dụng loại này")
    
    db.delete(seat_type)
    db.commit()
    return {"status": "success", "message": "Đã xóa loại ghế"}

# --- API LOẠI MÀN HÌNH ---
@app.get("/screen-types")
def get_screen_types(user=Depends(check_admin_role), db: Session = Depends(get_db)):
    """Lấy danh sách loại màn hình (2D, 3D, IMAX...)"""
    return db.query(models.ScreenType).all()

@app.post("/screen-types")
def add_screen_type(st: ScreenTypeCreate, user=Depends(check_admin_role), db: Session = Depends(get_db)):
    """Thêm loại màn hình mới"""
    new_st = models.ScreenType(name=st.name, surcharge=st.surcharge)
    db.add(new_st)
    db.commit()
    return {"status": "success", "message": f"Đã thêm loại màn hình: {st.name}"}

@app.put("/screen-types/{screen_type_id}")
def update_screen_type(screen_type_id: int, st: ScreenTypeCreate, user=Depends(check_admin_role), db: Session = Depends(get_db)):
    """Cập nhật loại màn hình"""
    screen_type = db.query(models.ScreenType).filter(models.ScreenType.screen_type_id == screen_type_id).first()
    if not screen_type:
        raise HTTPException(status_code=404, detail="Loại màn hình không tồn tại")
    
    screen_type.name = st.name
    screen_type.surcharge = st.surcharge
    db.commit()
    return {"status": "success", "message": f"Đã cập nhật loại màn hình: {st.name}"}

@app.delete("/screen-types/{screen_type_id}")
def delete_screen_type(screen_type_id: int, user=Depends(check_admin_role), db: Session = Depends(get_db)):
    """Xóa loại màn hình"""
    screen_type = db.query(models.ScreenType).filter(models.ScreenType.screen_type_id == screen_type_id).first()
    if not screen_type:
        raise HTTPException(status_code=404, detail="Loại màn hình không tồn tại")
    
    # Kiểm tra xem có phòng nào đang sử dụng loại này không
    screens_using = db.query(models.Screen).filter(models.Screen.screen_type_id == screen_type_id).count()
    if screens_using > 0:
        raise HTTPException(status_code=400, detail=f"Không thể xóa! Có {screens_using} phòng đang sử dụng loại này")
    
    db.delete(screen_type)
    db.commit()
    return {"status": "success", "message": "Đã xóa loại màn hình"}

@app.post("/seats/batch")
def add_seats_batch(batch: SeatBatchCreate, user=Depends(check_admin_role), db: Session = Depends(get_db)):
    count = 0
    for i in range(batch.start_number, batch.end_number + 1):
        exists = db.query(models.Seat).filter(
            models.Seat.screen_id == batch.screen_id,
            models.Seat.row_code == batch.row_code,
            models.Seat.seat_number == i
        ).first()
        
        if not exists:
            new_seat = models.Seat(
                screen_id=batch.screen_id,
                seat_type_id=batch.seat_type_id,
                row_code=batch.row_code,
                seat_number=i,
                is_active=True
            )
            db.add(new_seat)
            count += 1
            
    db.commit()
    return {"status": "success", "message": f"Đã thêm {count} ghế"}

@app.put("/seats/batch")
def update_seats_batch(batch: SeatBatchUpdate, user=Depends(check_admin_role), db: Session = Depends(get_db)):
    seats = db.query(models.Seat).filter(
        models.Seat.screen_id == batch.screen_id,
        models.Seat.row_code == batch.row_code,
        models.Seat.seat_number >= batch.start_number,
        models.Seat.seat_number <= batch.end_number
    ).all()
    
    count = 0
    for seat in seats:
        seat.seat_type_id = batch.seat_type_id
        seat.is_active = batch.is_active 
        count += 1
        
    db.commit()
    
    if count == 0:
        raise HTTPException(status_code=404, detail="Không tìm thấy ghế trong khoảng này để cập nhật.")
        
    return {"status": "success", "message": f"Đã cập nhật {count} ghế hàng {batch.row_code}"}

@app.get("/screens/{screen_id}/seats")
def get_screen_seats(screen_id: int, user=Depends(check_admin_role), db: Session = Depends(get_db)):
    return db.query(models.Seat).filter(models.Seat.screen_id == screen_id).all()

@app.put("/seats/{seat_id}")
def update_single_seat(seat_id: int, seat_update: SeatUpdate, user=Depends(check_admin_role), db: Session = Depends(get_db)):
    """Cập nhật một ghế riêng lẻ (loại ghế hoặc trạng thái)"""
    seat = db.query(models.Seat).filter(models.Seat.seat_id == seat_id).first()
    if not seat:
        raise HTTPException(status_code=404, detail="Ghế không tồn tại")
    
    if seat_update.seat_type_id is not None:
        seat.seat_type_id = seat_update.seat_type_id
    if seat_update.is_active is not None:
        seat.is_active = seat_update.is_active
    
    db.commit()
    return {"status": "success", "message": f"Đã cập nhật ghế {seat.row_code}{seat.seat_number}"}

# --- API BẮP NƯỚC ---
@app.get("/concessions")
def get_all_concessions(user=Depends(check_admin_role), db: Session = Depends(get_db)):
    return db.query(models.ConcessionItem).all()

@app.post("/concessions")
def add_concession(item: ConcessionCreate, user=Depends(check_admin_role), db: Session = Depends(get_db)):
    new_item = models.ConcessionItem(name=item.name, price=item.price)
    db.add(new_item)
    db.commit()
    return {"status": "success", "message": f"Đã thêm món: {item.name}"}

@app.delete("/concessions/{item_id}")
def delete_concession(item_id: int, user=Depends(check_admin_role), db: Session = Depends(get_db)):
    item = db.query(models.ConcessionItem).filter(models.ConcessionItem.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Món không tồn tại")
    db.delete(item)
    db.commit()
    return {"status": "success", "message": "Đã xóa món ăn"}

# --- BÁO CÁO DOANH THU ---
@app.get("/reports/revenue")
def get_revenue_report(user=Depends(check_admin_role), db: Session = Depends(get_db)):
    total_revenue = db.query(func.sum(models.Booking.total_amount))\
        .filter(models.Booking.status == "CONFIRMED").scalar() or 0

    total_bookings = db.query(models.Booking).filter(models.Booking.status == "CONFIRMED").count()

    revenue_by_movie = db.query(
        models.Movie.title, 
        func.sum(models.Booking.total_amount).label("revenue")
    ).join(models.Showtime, models.Movie.movie_id == models.Showtime.movie_id)\
     .join(models.Booking, models.Showtime.showtime_id == models.Booking.showtime_id)\
     .filter(models.Booking.status == "CONFIRMED")\
     .group_by(models.Movie.title)\
     .order_by(func.sum(models.Booking.total_amount).desc())\
     .all()

    revenue_by_cinema = db.query(
        models.Cinema.name,
        func.sum(models.Booking.total_amount).label("revenue")
    ).join(models.Screen, models.Cinema.cinema_id == models.Screen.cinema_id)\
     .join(models.Showtime, models.Screen.screen_id == models.Showtime.screen_id)\
     .join(models.Booking, models.Showtime.showtime_id == models.Booking.showtime_id)\
     .filter(models.Booking.status == "CONFIRMED")\
     .group_by(models.Cinema.name)\
     .order_by(func.sum(models.Booking.total_amount).desc())\
     .all()

    return {
        "total_revenue": float(total_revenue),
        "total_orders": total_bookings,
        "by_movie": [{"title": r[0], "revenue": float(r[1])} for r in revenue_by_movie],
        "by_cinema": [{"name": r[0], "revenue": float(r[1])} for r in revenue_by_cinema],
        "report_date": datetime.now()
    }
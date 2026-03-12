from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from pydantic import BaseModel
import models
from database import engine, get_db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Catalog Service")

# --- Schemas ---
class SeatBatchRequest(BaseModel):
    seat_ids: List[int]

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

@app.get("/")
def health_check():
    return {"status": "Catalog Service is running"}

@app.get("/movies")
def get_movies(status: str = None, search: str = None, db: Session = Depends(get_db)):
    """
    API lấy danh sách phim.
    - status: Lọc theo trạng thái (NOW_SHOWING, COMING_SOON)
    - search: Lọc theo tên phim (Tìm gần đúng - Like)
    """
    query = db.query(models.Movie)
    
    if status:
        query = query.filter(models.Movie.status == status)
        
    if search:
        query = query.filter(models.Movie.title.ilike(f"%{search}%"))
        
    return query.all()

@app.get("/movies/{movie_id}")
def get_movie_detail(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(models.Movie).filter(models.Movie.movie_id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {
        "movie_id": movie.movie_id,
        "title": movie.title,
        "duration_minutes": movie.duration_minutes,
        "status": movie.status,
        "poster_url": movie.poster_url,
        "director": movie.director,
        "actors": movie.actors,
        "genre": movie.genre,
        "release_date": str(movie.release_date) if movie.release_date else None,
        "language": movie.language,
        "age_rating": movie.age_rating,
        "description": movie.description
    }

@app.get("/movies/{movie_id}/showtimes")
def get_movie_showtimes(movie_id: int, db: Session = Depends(get_db)):
    showtimes = db.query(models.Showtime)\
        .options(joinedload(models.Showtime.screen).joinedload(models.Screen.cinema))\
        .filter(models.Showtime.movie_id == movie_id)\
        .all()
    
    results = []
    for st in showtimes:
        # Get screen type info
        screen_type = db.query(models.ScreenType).filter(
            models.ScreenType.screen_type_id == st.screen.screen_type_id
        ).first() if st.screen.screen_type_id else None
        
        results.append({
            "showtime_id": st.showtime_id,
            "start_time": st.start_time,
            "base_price": st.base_price,
            "screen_id": st.screen_id,
            "screen_name": st.screen.name,
            "cinema_name": st.screen.cinema.name,
            "cinema_id": st.screen.cinema.cinema_id,
            "screen_type_name": screen_type.name if screen_type else "2D",
            "screen_type_surcharge": float(screen_type.surcharge) if screen_type else 0
        })
    return results

@app.get("/showtimes/{showtime_id}")
def get_showtime_detail(showtime_id: int, db: Session = Depends(get_db)):
    """
    API lấy chi tiết một suất chiếu.
    Quan trọng: Cần trả về screen_id để Booking Service tra cứu sơ đồ ghế.
    """
    st = db.query(models.Showtime)\
        .options(joinedload(models.Showtime.movie), joinedload(models.Showtime.screen).joinedload(models.Screen.cinema))\
        .filter(models.Showtime.showtime_id == showtime_id)\
        .first()
        
    if not st:
        raise HTTPException(status_code=404, detail="Showtime not found")
    
    # Get screen type info
    screen_type = db.query(models.ScreenType).filter(
        models.ScreenType.screen_type_id == st.screen.screen_type_id
    ).first() if st.screen.screen_type_id else None
        
    return {
        "showtime_id": st.showtime_id,
        "movie_title": st.movie.title,
        "cinema_name": st.screen.cinema.name,
        "screen_name": st.screen.name,
        "screen_id": st.screen_id, 
        "start_time": st.start_time,
        "poster_url": st.movie.poster_url,
        "base_price": float(st.base_price),
        "screen_type_name": screen_type.name if screen_type else "2D",
        "screen_type_surcharge": float(screen_type.surcharge) if screen_type else 0
    }

@app.get("/screens/{screen_id}/seats")
def get_screen_seats(screen_id: int, db: Session = Depends(get_db)):
    """Trả về danh sách ghế kèm loại và trạng thái active"""
    seats = db.query(models.Seat).filter(models.Seat.screen_id == screen_id).all()
    return seats

@app.post("/seats/batch")
def get_seats_batch(req: SeatBatchRequest, db: Session = Depends(get_db)):
    """Lấy thông tin nhiều ghế theo danh sách seat_ids"""
    seats = db.query(models.Seat).filter(models.Seat.seat_id.in_(req.seat_ids)).all()
    return [
        {
            "seat_id": s.seat_id,
            "row_code": s.row_code,
            "seat_number": s.seat_number,
            "label": f"{s.row_code}{s.seat_number}"
        }
        for s in seats
    ]

@app.get("/concessions")
def get_concessions(db: Session = Depends(get_db)):
    return db.query(models.ConcessionItem).all()

@app.get("/seat-types")
def get_seat_types(db: Session = Depends(get_db)):
    return db.query(models.SeatType).all()

@app.get("/screen-types")
def get_screen_types(db: Session = Depends(get_db)):
    """Lấy danh sách các loại màn hình (2D, 3D, IMAX...)"""
    return db.query(models.ScreenType).all()

@app.get("/screens/{screen_id}")
def get_screen_detail(screen_id: int, db: Session = Depends(get_db)):
    """Lấy thông tin chi tiết của phòng chiếu"""
    screen = db.query(models.Screen).filter(models.Screen.screen_id == screen_id).first()
    if not screen:
        raise HTTPException(status_code=404, detail="Screen not found")
    
    screen_type = db.query(models.ScreenType).filter(
        models.ScreenType.screen_type_id == screen.screen_type_id
    ).first() if screen.screen_type_id else None
    
    return {
        "screen_id": screen.screen_id,
        "name": screen.name,
        "total_seats": screen.total_seats,
        "rows_count": screen.rows_count,
        "cols_count": screen.cols_count,
        "screen_type_id": screen.screen_type_id,
        "screen_type_name": screen_type.name if screen_type else "2D",
        "screen_type_surcharge": float(screen_type.surcharge) if screen_type else 0
    }
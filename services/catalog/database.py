import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://user:password@db:3306/movie_booking_db?charset=utf8mb4"

def create_engine_with_retry(max_retries=10, delay=5):
    """
    Cố gắng kết nối đến Database nhiều lần trước khi bỏ cuộc.
    - max_retries: Số lần thử tối đa (mặc định 10 lần)
    - delay: Thời gian nghỉ giữa các lần thử (giây)
    """
    retries = 0
    while retries < max_retries:
        try:
            engine = create_engine(DATABASE_URL)
            
            with engine.connect() as connection:
                print(f"✅ Kết nối Database thành công tại {DATABASE_URL}")
                return engine
                
        except OperationalError as e:
            retries += 1
            print(f"⏳ Database chưa sẵn sàng (Lần {retries}/{max_retries}). Đang chờ {delay}s... Lỗi: {e}")
            time.sleep(delay)
            
    raise Exception("❌ Không thể kết nối đến Database sau nhiều lần thử. Vui lòng kiểm tra Docker container 'db'.")

engine = create_engine_with_retry()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
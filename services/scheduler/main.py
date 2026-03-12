import time
import schedule
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from datetime import datetime, timedelta

TIMEOUT_MINUTES = 2

def job_release_seats():
    print(f"--- [SCHEDULER] Chạy quét lúc {datetime.now()} ---")
    db = SessionLocal()
    try:
        # 1. Tính thời điểm giới hạn
        time_threshold = datetime.now() - timedelta(minutes=TIMEOUT_MINUTES)
        
        # 2. Tìm các đơn PENDING quá hạn
        expired_bookings = db.query(models.Booking).filter(
            models.Booking.status == "PENDING",
            models.Booking.booking_date < time_threshold
        ).all()
        
        if not expired_bookings:
            print("Không có đơn hàng nào quá hạn.")
            return

        # 3. Hủy đơn
        count = 0
        for booking in expired_bookings:
            print(f"-> Hủy Booking ID: {booking.booking_id} (Tạo lúc: {booking.booking_date})")
            booking.status = "CANCELLED"
            count += 1
        
        db.commit()
        print(f"Đã hủy thành công {count} đơn hàng.")
        
    except Exception as e:
        print(f"Lỗi Scheduler: {e}")
    finally:
        db.close()

# --- CẤU HÌNH LỊCH CHẠY ---
schedule.every(30).seconds.do(job_release_seats)

if __name__ == "__main__":
    print("🚀 Scheduler Service đang chạy...")
    print(f"Quy tắc: Hủy đơn PENDING sau {TIMEOUT_MINUTES} phút.")
    
    while True:
        schedule.run_pending()
        time.sleep(1)
from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, BigInteger
from database import Base
import datetime

class Transaction(Base):
    __tablename__ = "transactions"

    # Khóa chính (BigInteger để chứa số lượng giao dịch lớn)
    transaction_id = Column(BigInteger, primary_key=True, index=True)

    # Logical FK: Chỉ lưu ID của Booking, không nối khóa ngoại cứng
    # (Vì bảng Bookings nằm ở database khác)
    booking_id = Column(BigInteger, nullable=False, index=True)

    # Số tiền giao dịch (Dùng DECIMAL để chính xác tuyệt đối)
    amount = Column(DECIMAL(10, 2), nullable=False)

    # Loại giao dịch: 'PAYMENT' (Thu tiền) hoặc 'REFUND' (Hoàn tiền)
    transaction_type = Column(String(50), nullable=False) 

    # Trạng thái: 'PENDING', 'SUCCESS', 'FAILED'
    status = Column(String(50), default="PENDING")

    # Mã tham chiếu từ cổng thanh toán (Ví dụ: Mã giao dịch Momo/ZaloPay trả về)
    # Dùng để tra soát (Reconciliation) sau này
    gateway_ref_id = Column(String(100), nullable=True)

    # Thời gian tạo giao dịch
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    payment_method = Column(String(50), nullable=True) # MOMO, VISA...
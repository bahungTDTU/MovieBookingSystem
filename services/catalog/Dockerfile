# Sử dụng Python 3.9 nhẹ
FROM python:3.9-slim

# Thiết lập thư mục làm việc bên trong container
WORKDIR /app

# Copy file requirements và cài đặt thư viện
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code vào container
COPY . .

# Mở port 8001 (Catalog Service sẽ chạy ở port này)
EXPOSE 8001

# Lệnh chạy server khi container khởi động
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
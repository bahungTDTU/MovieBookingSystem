FROM python:3.9-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy file requirements và cài đặt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code
COPY . .

# Mở port 8006 (Dành riêng cho Redemption Service)
EXPOSE 8006

# Chạy server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8006"]
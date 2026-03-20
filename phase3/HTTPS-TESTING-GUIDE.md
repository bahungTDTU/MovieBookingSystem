# 🔐 Phase 3 - HTTPS Testing Guide (AWS EC2 Production Server)

## 📋 Server Information

**AWS EC2 Instance:**
- **Instance ID:** i-0df95b6e95fa595ef
- **Instance Name:** Cineworld-phase2-new
- **Public IP:** 13.219.51.85
- **Public DNS:** ec2-13-219-51-85.ap-southeast-1.compute.amazonaws.com
- **Region:** ap-southeast-1 (Singapore)
- **SSH Key:** `C:\Users\Nguyen Long\.ssh\cineworld-key1.pem`
- **OS:** Ubuntu 22.04
- **Phase 2 Setup:** ✅ MySQL, Nginx, systemd services, Let's Encrypt SSL (nếu có domain)

---

## 🎯 Phase 3 Deployment Strategy

### Mục tiêu:
- ✅ Giữ lại Nginx reverse proxy từ Phase 2
- ✅ Stop các systemd services
- ✅ Deploy Docker containers
- ✅ Update Nginx upstream targets: `127.0.0.1:800X` → `localhost:800X` (Docker ports)
- ✅ **HTTPS vẫn hoạt động** với Let's Encrypt certificate

### Architecture Phase 3:
```
Client → AWS Security Group (80, 443)
         → Nginx (HTTPS termination)
            → Docker Network
               ├── catalog_service (8001)
               ├── otp_service (8002)
               ├── identity_service (8003)
               ├── booking_service (8004)
               ├── payment_service (8005)
               ├── redemption_service (8006)
               ├── management_service (8007)
               ├── scheduler_service (background)
               ├── frontend (3000→80)
               └── mysql (3306) + volume
```

---

## 📦 BƯỚC 1: Push Docker Images lên Docker Hub

**⏱️ Thời gian:** ~10-15 phút (tùy tốc độ mạng)

### 1.1. Tạo Docker Hub Account (nếu chưa có)

1. Truy cập: https://hub.docker.com/signup
2. Tạo account và xác nhận email
3. Ghi nhớ Docker Hub username

### 1.2. Login vào Docker Hub

**Trên Windows PowerShell:**

```powershell
# Di chuyển vào thư mục dự án
cd "C:\Users\Nguyen Long\Downloads\MovieBookingSystem (2)"

# Login Docker Hub
docker login

# Nhập username và password khi được yêu cầu
```

### 1.3. Tag và Push Tất Cả Images

```powershell
# ⚠️ THAY "your-dockerhub-username" BẰNG USERNAME CỦA BẠN
$USERNAME = "your-dockerhub-username"

Write-Host "Tagging images..." -ForegroundColor Green

docker tag moviebookingsystem2-catalog_service ${USERNAME}/cineworld-catalog:latest
docker tag moviebookingsystem2-identity_service ${USERNAME}/cineworld-identity:latest
docker tag moviebookingsystem2-otp_service ${USERNAME}/cineworld-otp:latest
docker tag moviebookingsystem2-booking_service ${USERNAME}/cineworld-booking:latest
docker tag moviebookingsystem2-payment_service ${USERNAME}/cineworld-payment:latest
docker tag moviebookingsystem2-redemption_service ${USERNAME}/cineworld-redemption:latest
docker tag moviebookingsystem2-management_service ${USERNAME}/cineworld-management:latest
docker tag moviebookingsystem2-scheduler_service ${USERNAME}/cineworld-scheduler:latest
docker tag moviebookingsystem2-frontend ${USERNAME}/cineworld-frontend:latest

Write-Host "Pushing images to Docker Hub (this will take 5-10 minutes)..." -ForegroundColor Yellow

docker push ${USERNAME}/cineworld-catalog:latest
docker push ${USERNAME}/cineworld-identity:latest
docker push ${USERNAME}/cineworld-otp:latest
docker push ${USERNAME}/cineworld-booking:latest
docker push ${USERNAME}/cineworld-payment:latest
docker push ${USERNAME}/cineworld-redemption:latest
docker push ${USERNAME}/cineworld-management:latest
docker push ${USERNAME}/cineworld-scheduler:latest
docker push ${USERNAME}/cineworld-frontend:latest

Write-Host "All images pushed successfully!" -ForegroundColor Green
Write-Host "Verify at: https://hub.docker.com/u/$USERNAME" -ForegroundColor Cyan
```

### 1.4. Verify trên Docker Hub

1. Truy cập: `https://hub.docker.com/u/your-username/`
2. Kiểm tra có 9 repositories:
   - ✅ cineworld-catalog
   - ✅ cineworld-identity
   - ✅ cineworld-otp
   - ✅ cineworld-booking
   - ✅ cineworld-payment
   - ✅ cineworld-redemption
   - ✅ cineworld-management
   - ✅ cineworld-scheduler
   - ✅ cineworld-frontend

---

## 🚀 BƯỚC 2: Tạo Production docker-compose.yml

**File này sẽ pull images từ Docker Hub thay vì build local.**

### 2.1. Tạo file docker-compose.prod.yml

**Trên Windows, trong thư mục dự án:**

```powershell
code docker-compose.prod.yml
```

**Nội dung file (⚠️ THAY your-dockerhub-username):**

```yaml
version: '3.8'

services:
  # Database
  db:
    image: mysql:8.0
    container_name: movie_mysql_container
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p$${MYSQL_ROOT_PASSWORD}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Adminer
  adminer:
    image: adminer:latest
    container_name: movie_adminer
    restart: always
    ports:
      - "8888:8080"
    depends_on:
      - db

  # Catalog Service - PULL FROM DOCKER HUB
  catalog_service:
    image: your-dockerhub-username/cineworld-catalog:latest
    container_name: movie_catalog_service
    restart: always
    env_file:
      - .env
    ports:
      - "8001:8001"
    depends_on:
      db:
        condition: service_healthy

  # OTP Service
  otp_service:
    image: your-dockerhub-username/cineworld-otp:latest
    container_name: movie_otp_service
    restart: always
    env_file:
      - .env
    ports:
      - "8002:8002"
    depends_on:
      db:
        condition: service_healthy

  # Identity Service
  identity_service:
    image: your-dockerhub-username/cineworld-identity:latest
    container_name: movie_identity_service
    restart: always
    env_file:
      - .env
    ports:
      - "8003:8003"
    depends_on:
      db:
        condition: service_healthy

  # Booking Service
  booking_service:
    image: your-dockerhub-username/cineworld-booking:latest
    container_name: movie_booking_service
    restart: always
    env_file:
      - .env
    ports:
      - "8004:8004"
    depends_on:
      db:
        condition: service_healthy

  # Payment Service
  payment_service:
    image: your-dockerhub-username/cineworld-payment:latest
    container_name: movie_payment_service
    restart: always
    env_file:
      - .env
    ports:
      - "8005:8005"
    depends_on:
      db:
        condition: service_healthy

  # Redemption Service
  redemption_service:
    image: your-dockerhub-username/cineworld-redemption:latest
    container_name: movie_redemption_service
    restart: always
    env_file:
      - .env
    ports:
      - "8006:8006"
    depends_on:
      db:
        condition: service_healthy

  # Management Service
  management_service:
    image: your-dockerhub-username/cineworld-management:latest
    container_name: movie_management_service
    restart: always
    env_file:
      - .env
    ports:
      - "8007:8007"
    depends_on:
      db:
        condition: service_healthy

  # Scheduler Service
  scheduler_service:
    image: your-dockerhub-username/cineworld-scheduler:latest
    container_name: movie_scheduler_service
    restart: always
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy

  # Frontend
  frontend:
    image: your-dockerhub-username/cineworld-frontend:latest
    container_name: movie_frontend
    restart: always
    ports:
      - "3000:80"

volumes:
  mysql_data:
```

---

## 🔌 BƯỚC 3: SSH vào AWS EC2 Server

**⏱️ Thời gian:** ~1 phút

### 3.1. SSH từ Windows PowerShell

```powershell
# SSH với PEM key
ssh -i "C:\Users\Nguyen Long\.ssh\cineworld-key1.pem" ubuntu@13.219.51.85
```

**Nếu gặp lỗi "Bad permissions":**

```powershell
# Run PowerShell as Administrator, chạy:
icacls "C:\Users\Nguyen Long\.ssh\cineworld-key1.pem" /inheritance:r
icacls "C:\Users\Nguyen Long\.ssh\cineworld-key1.pem" /grant:r "$($env:USERNAME):(R)"
```

### 3.2. Alternative: Dùng Git Bash

**Trong Git Bash:**

```bash
chmod 400 "/c/Users/Nguyen Long/.ssh/cineworld-key1.pem"
ssh -i "/c/Users/Nguyen Long/.ssh/cineworld-key1.pem" ubuntu@13.219.51.85
```

### 3.3. First Time Login

```bash
# Check current user
whoami
# Output: ubuntu

# Check OS version
lsb_release -a
# Output: Ubuntu 22.04

# Check current working directory
pwd
# Output: /home/ubuntu
```

---

## 🐳 BƯỚC 4: Kiểm tra & Cài Docker (nếu cần)

**⏱️ Thời gian:** ~5 phút

**Trên server (sau khi SSH):**

### 4.1. Check Docker đã cài chưa

```bash
docker --version
docker-compose --version
```

### 4.2. Nếu chưa có Docker, cài đặt:

```bash
# Download installation script
curl -fsSL https://get.docker.com -o get-docker.sh

# Run installation
sudo sh get-docker.sh

# Add ubuntu user vào docker group
sudo usermod -aG docker ubuntu

# Apply group membership (hoặc logout/login lại)
newgrp docker

# Enable Docker auto-start on boot
sudo systemctl enable docker
sudo systemctl start docker

# Verify installation
docker run hello-world
```

### 4.3. Cài Docker Compose (nếu cần)

```bash
# Docker Desktop thường đi kèm docker-compose
# Nếu không có:
sudo apt update
sudo apt install docker-compose-plugin -y

# Verify
docker compose version
```

---

## 🛑 BƯỚC 5: Stop Phase 2 systemd Services

**⏱️ Thời gian:** ~2 phút

**Trên server:**

### 5.1. Check services đang chạy

```bash
systemctl list-units --type=service --state=running | grep cineworld
```

### 5.2. Stop tất cả services

```bash
# Stop all Phase 2 services
sudo systemctl stop cineworld-catalog
sudo systemctl stop cineworld-otp
sudo systemctl stop cineworld-identity
sudo systemctl stop cineworld-booking
sudo systemctl stop cineworld-payment
sudo systemctl stop cineworld-redemption
sudo systemctl stop cineworld-management
sudo systemctl stop cineworld-scheduler

# Hoặc dùng loop:
for service in catalog otp identity booking payment redemption management scheduler; do
    sudo systemctl stop cineworld-$service
    sudo systemctl disable cineworld-$service
done
```

### 5.3. Verify tất cả đã stop

```bash
systemctl list-units --type=service --state=running | grep cineworld
```

**Expected:** Không còn service nào chạy.

### 5.4. Check ports đã free

```bash
# Ports 8001-8007 phải free cho Docker
sudo netstat -tlnp | grep 800

# Nếu có process nào còn chiếm port, kill nó
# sudo kill <pid>
```

---

## 📁 BƯỚC 6: Upload Files lên Server

**⏱️ Thời gian:** ~3 phút

### 6.1. Option A: Dùng SCP (Recommended)

**Trên Windows PowerShell (mở terminal MỚI, không phải SSH session):**

```powershell
# Navigate to project directory
cd "C:\Users\Nguyen Long\Downloads\MovieBookingSystem (2)"

# Upload docker-compose production file
scp -i "C:\Users\Nguyen Long\.ssh\cineworld-key1.pem" `
    docker-compose.prod.yml `
    ubuntu@13.219.51.85:/home/ubuntu/

# Upload .env file
scp -i "C:\Users\Nguyen Long\.ssh\cineworld-key1.pem" `
    .env `
    ubuntu@13.219.51.85:/home/ubuntu/

# Upload database init script
scp -i "C:\Users\Nguyen Long\.ssh\cineworld-key1.pem" `
    -r database `
    ubuntu@13.219.51.85:/home/ubuntu/

# Upload Nginx config for Phase 3
scp -i "C:\Users\Nguyen Long\.ssh\cineworld-key1.pem" `
    phase3\nginx-production-docker.conf `
    ubuntu@13.219.51.85:/home/ubuntu/
```

### 6.2. Option B: Dùng Git

**Nếu code đã push lên GitHub, trên server:**

```bash
# Clone repo
cd /home/ubuntu
git clone https://github.com/bahungTDTU/MovieBookingSystem.git
cd MovieBookingSystem

# Hoặc nếu đã có repo:
cd /home/ubuntu/MovieBookingSystem
git pull origin main
```

### 6.3. Verify files đã upload

**Trên server:**

```bash
cd /home/ubuntu
ls -la

# Should see:
# - docker-compose.prod.yml
# - .env
# - database/
# - nginx-production-docker.conf
```

---

## 🔧 BƯỚC 7: Cập nhật Nginx Config cho Docker

**⏱️ Thời gian:** ~3 phút

**Trên server (SSH session):**

### 7.1. Backup config Phase 2

```bash
sudo cp /etc/nginx/sites-available/cineworld /etc/nginx/sites-available/cineworld.phase2.backup

# Verify backup
ls -la /etc/nginx/sites-available/
```

### 7.2. Check domain hiện tại (từ Phase 2)

```bash
grep "server_name" /etc/nginx/sites-available/cineworld
```

**2 scenarios:**

**Scenario 1: Có domain thật (ví dụ: cineworld.example.com)**
- ✅ Let's Encrypt SSL đã setup
- ✅ HTTPS sẽ hoạt động ngay

**Scenario 2: Chỉ có IP (13.219.51.85)**
- ⚠️ SSL với IP cần self-signed cert hoặc skip
- ⚠️ Browser sẽ warning

### 7.3. Update Nginx config cho Docker

```bash
# Copy Phase 3 config
sudo cp /home/ubuntu/nginx-production-docker.conf /etc/nginx/sites-available/cineworld

# Update domain/IP
# Nếu Phase 2 dùng domain:
sudo sed -i 's/YOUR_DOMAIN/yourdomain.com/g' /etc/nginx/sites-available/cineworld

# Nếu Phase 2 dùng IP:
sudo sed -i 's/YOUR_DOMAIN/13.219.51.85/g' /etc/nginx/sites-available/cineworld

# Hoặc edit manual:
sudo nano /etc/nginx/sites-available/cineworld
# Tìm và thay YOUR_DOMAIN bằng domain/IP của bạn
```

### 7.4. Test và Reload Nginx

```bash
# Test config syntax
sudo nginx -t

# Expected output:
# nginx: configuration file /etc/nginx/nginx.conf test is successful

# Reload Nginx
sudo systemctl reload nginx

# Check status
sudo systemctl status nginx
```

**Lưu ý:** Nginx vẫn chạy và serve HTTPS, nhưng upstream targets giờ trỏ vào Docker containers.

---

## 🐋 BƯỚC 8: Start Docker Containers

**⏱️ Thời gian:** ~5-7 phút (pull images từ Docker Hub)

**Trên server:**

### 8.1. Edit docker-compose.prod.yml để update username

```bash
cd /home/ubuntu

# Update Docker Hub username trong file
# Thay "your-dockerhub-username" bằng username thật
nano docker-compose.prod.yml
```

**Hoặc dùng sed:**

```bash
sed -i 's/your-dockerhub-username/actual-username/g' docker-compose.prod.yml
```

### 8.2. Verify .env file

```bash
cat .env

# Phải có:
# - MYSQL credentials
# - SMTP credentials (nếu muốn send email)
# - DATABASE_URL=mysql+pymysql://user:password@db:3306/movie_booking_db
```

### 8.3. Pull images từ Docker Hub

```bash
docker-compose -f docker-compose.prod.yml pull
```

**Expected:** Download tất cả 9 images từ Docker Hub

### 8.4. Start containers

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 8.5. Monitor startup

```bash
# Watch logs (optional)
docker-compose -f docker-compose.prod.yml logs -f

# Press Ctrl+C to exit

# Check container status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Wait until all are "Up" (might take 30-60 seconds)
```

### 8.6. Verify all 11 containers running

```bash
docker ps | wc -l
# Should be 12 (11 containers + header line)
```

---

## ✅ BƯỚC 9: Test HTTPS & Application

**⏱️ Thời gian:** ~5 phút

### 9.1. Test trên Server với curl

**Trên server (SSH session):**

```bash
# Test HTTP → HTTPS redirect
curl -I http://localhost
# Expected: 301 Moved Permanently, Location: https://

# Test HTTPS homepage (với domain)
curl -I https://yourdomain.com
# Expected: 200 OK

# Hoặc với IP (skip SSL verification):
curl -k -I https://13.219.51.85
# Expected: 200 OK

# Test Catalog API
curl -k https://13.219.51.85/api/catalog/movies | jq '.[0]'
# Expected: JSON with movie data

# Test Identity API
curl -k https://13.219.51.85/api/identity/
# Expected: {"message": "Identity Service", ...}

# Test Booking health
curl -k https://13.219.51.85/api/booking/health
# Expected: {"status": "healthy"}

# Test Payment API
curl -k https://13.219.51.85/api/payment/
# Expected: Payment service message
```

### 9.2. Test từ Windows Browser

**Mở browser trên Windows:**

**Nếu có domain từ Phase 2:**
```
https://yourdomain.com
```

**Nếu chỉ có IP:**
```
https://13.219.51.85
```

**⚠️ Lưu ý với IP:**
- Browser sẽ warning "Not Secure" hoặc "Certificate Error"
- Vì SSL certificate được issue cho domain, không phải IP
- Click "Advanced" → "Proceed anyway"

**Expected:**
- ✅ Homepage loads successfully
- ✅ Movies display từ database
- ✅ Search bar hoạt động
- ✅ Can navigate các pages

### 9.3. Test API Endpoints

```
https://13.219.51.85/api/catalog/docs
https://13.219.51.85/api/identity/docs
https://13.219.51.85/api/booking/docs
https://13.219.51.85/api/payment/docs
```

### 9.4. Test Adminer (Database)

```
http://13.219.51.85:8888
```

**Login:**
- Server: db
- Username: user
- Password: password
- Database: movie_booking_db

### 9.5. Test Full Booking Flow

1. Register account → Verify OTP
2. Browse movies
3. Select showtime
4. Choose seats
5. Add concessions
6. Complete payment
7. Check "My Tickets"

---

## 🎥 VIDEO DEMO: Phase 3 Production Deployment

### **VIDEO 13: Deploy to AWS & Test HTTPS** ⏱️ ~10 phút

#### **Part 1: Push Images to Docker Hub** (~2 min)

**[On Windows PowerShell]**

**[THOẠI]:**
> "For Phase 3, Docker images must be pushed to Docker Hub registry so they can be pulled on the production server. Let me login and push all 9 images."

```powershell
# Show current images
docker images | Select-String "moviebookingsystem2"

# Login
docker login

# Tag and push (show 2-3 examples)
$USERNAME = "your-username"
docker tag moviebookingsystem2-catalog_service ${USERNAME}/cineworld-catalog:latest
docker push ${USERNAME}/cineworld-catalog:latest
```

**[THOẠI]:**
> "I've pushed all images to Docker Hub. This took about 10 minutes for all 9 services."

**[Show Docker Hub repo page in browser]**

**[THOẠI]:**
> "Here you can see all 9 repositories on Docker Hub. Each image is tagged as 'latest' and ready to be pulled."

---

#### **Part 2: Connect to AWS Server** (~1 min)

**[THOẠI]:**
> "Now let's connect to our AWS EC2 instance that was configured in Phase 2."

```powershell
ssh -i "C:\Users\Nguyen Long\.ssh\cineworld-key1.pem" ubuntu@13.219.51.85
```

**[THOẠI]:**
> "I'm now connected to the Ubuntu server. Let's check the current Phase 2 deployment."

```bash
# Show Phase 2 services
systemctl list-units --type=service --state=running | grep cineworld

# Show current processes
ps aux | grep uvicorn
```

**[THOẠI]:**
> "Phase 2 is running with 8 systemd services. We'll transition these to Docker containers."

---

#### **Part 3: Stop Phase 2 Services** (~1 min)

**[THOẠI]:**
> "First, we need to stop all Phase 2 systemd services to free up the ports for Docker."

```bash
# Stop services
for service in catalog otp identity booking payment redemption management scheduler; do
    sudo systemctl stop cineworld-$service
    sudo systemctl disable cineworld-$service
done

# Verify all stopped
systemctl list-units --type=service --state=running | grep cineworld

# Check ports are free
sudo netstat -tlnp | grep 800
```

**[THOẠI]:**
> "All Phase 2 services stopped. Ports 8001 through 8007 are now free for Docker containers."

---

#### **Part 4: Verify Files & Update Nginx** (~1.5 min)

**[THOẠI]:**
> "Let me verify the deployment files and update the Nginx configuration."

```bash
# List uploaded files
cd /home/ubuntu
ls -la

# Show docker-compose file
cat docker-compose.prod.yml | head -30

# Backup Phase 2 Nginx config
sudo cp /etc/nginx/sites-available/cineworld /etc/nginx/sites-available/cineworld.phase2.backup

# Copy Phase 3 config
sudo cp nginx-production-docker.conf /etc/nginx/sites-available/cineworld

# Check current domain
grep "server_name" /etc/nginx/sites-available/cineworld
```

**[THOẠI]:**
> "I need to update the domain in the Nginx config. Let me check what domain was used in Phase 2."

```bash
# Show Phase 2 config
grep "server_name" /etc/nginx/sites-available/cineworld.phase2.backup

# Update new config with same domain
# (Use actual domain from Phase 2)
sudo sed -i 's/YOUR_DOMAIN/yourdomain.com/g' /etc/nginx/sites-available/cineworld

# Test Nginx config
sudo nginx -t

# Reload
sudo systemctl reload nginx
```

**[THOẠI]:**
> "Nginx configuration updated and reloaded. The upstream targets now point to Docker containers on localhost ports."

---

#### **Part 5: Start Docker Containers** (~2 min)

**[THOẠI]:**
> "Now let's pull the images from Docker Hub and start all containers."

```bash
# Pull images
docker-compose -f docker-compose.prod.yml pull
```

**[THOẠI]:**
> "Docker is downloading all 9 images from Docker Hub. This demonstrates that we're pulling pre-built images, not building locally - which is a key Phase 3 requirement."

```bash
# Start containers
docker-compose -f docker-compose.prod.yml up -d

# Wait a moment
sleep 5

# Check status
docker ps --format "table {{.Names}}\t{{.Status}}"
```

**[THOẠI]:**
> "All 11 containers are now running! The database, 8 microservices, frontend, and Adminer."

---

#### **Part 6: Test HTTPS** (~2.5 min)

**[THOẠI]:**
> "The critical test: Does HTTPS still work after transitioning from systemd to Docker? Let's find out."

```bash
# Test HTTP redirect
curl -I http://13.219.51.85

# Test HTTPS
curl -k -I https://13.219.51.85

# Test APIs
curl -k https://13.219.51.85/api/catalog/movies | jq '.[0]'
curl -k https://13.219.51.85/api/identity/
```

**[THOẠI]:**
> "All tests successful! HTTPS is working. The Nginx reverse proxy correctly forwards HTTPS requests to Docker containers. Now let's verify in the browser."

**[Switch to browser on Windows]**

```
https://13.219.51.85
```

**Or with domain:**
```
https://yourdomain.com
```

**[THOẠI]:**
> "The application loads successfully over HTTPS. Let me check the SSL certificate."

**[Click lock icon → Certificate]**

**[THOẠI]:**
> "The certificate is issued by Let's Encrypt, valid, and trusted by the browser. HTTPS is fully functional."

**[Test API docs]**

```
https://13.219.51.85/api/catalog/docs
```

**[THOẠI]:**
> "Swagger API documentation accessible via HTTPS. Let's test an endpoint."

**[Click GET /movies → Try it out → Execute]**

**[THOẠI]:**
> "Perfect! The API returns movie data over HTTPS."

---

#### **Part 7: Verify End-to-End** (~1 min)

**[THOẠI]:**
> "Finally, let's verify a complete booking works."

**[Quick demo:]**
1. Navigate homepage
2. Select a movie
3. Choose seat
4. Show booking summary

**[THOẠI]:**
> "Everything works perfectly! Phase 3 deployment complete. We've successfully transitioned from Phase 2's systemd services to Phase 3's Docker containers while maintaining full HTTPS functionality through Nginx reverse proxy."

---

## 📊 Verification Checklist

**Trên Server:**

```bash
# ✅ All containers running
docker ps | wc -l

# ✅ Nginx running
sudo systemctl status nginx

# ✅ Phase 2 services stopped
systemctl list-units | grep cineworld | grep running

# ✅ Docker auto-start enabled
sudo systemctl is-enabled docker

# ✅ Containers have restart policy
docker inspect movie_catalog_service --format='{{.HostConfig.RestartPolicy.Name}}'

# ✅ Database volume exists
docker volume ls | grep mysql

# ✅ HTTPS working
curl -k -I https://13.219.51.85
```

**Từ Windows Browser:**

- ✅ `https://13.219.51.85` loads (hoặc domain)
- ✅ Lock icon có hiện (với domain + Let's Encrypt)
- ✅ APIs accessible: `/api/catalog/docs`
- ✅ Adminer: `http://13.219.51.85:8888`
- ✅ Booking flow hoạt động

---

## 🔐 SSL Certificate Details

### Nếu dùng Let's Encrypt từ Phase 2:

```bash
# Check certificate status
sudo certbot certificates

# Verify auto-renewal
sudo certbot renew --dry-run

# Certificate location
ls -la /etc/letsencrypt/live/yourdomain.com/
```

### Nếu chưa có SSL (chỉ dùng IP):

**Option 1: Setup domain mới** (Recommended)

```bash
# 1. Mua domain (Namecheap, Cloudflare, etc.)
# 2. Point A record to: 13.219.51.85
# 3. Wait for DNS propagation (~5-10 minutes)

# 4. Get Let's Encrypt certificate
sudo certbot --nginx -d yourdomain.com --email your@email.com --agree-tos --no-eff-email --redirect

# 5. Test
curl -I https://yourdomain.com
```

**Option 2: Accept SSL warning với IP** (Demo only)

- Browser sẽ warning về certificate mismatch
- Click "Advanced" → "Proceed anyway"
- HTTPS vẫn encrypt traffic nhưng không verified

---

## 🚨 Troubleshooting

### Issue 1: SSH Permission Denied

**Trên Windows:**

```powershell
# Fix PEM file permissions
icacls "C:\Users\Nguyen Long\.ssh\cineworld-key1.pem" /inheritance:r
icacls "C:\Users\Nguyen Long\.ssh\cineworld-key1.pem" /grant:r "$($env:USERNAME):(R)"

# Retry SSH
ssh -i "C:\Users\Nguyen Long\.ssh\cineworld-key1.pem" ubuntu@13.219.51.85
```

### Issue 2: Container won't start

```bash
# Check logs
docker logs movie_catalog_service

# Common issues:
# - Database not ready: wait 30s
# - .env missing: check file exists
# - Image pull failed: verify Docker Hub username
```

### Issue 3: Nginx 502 Bad Gateway

```bash
# Verify containers running
docker ps

# Check if service listening
curl http://localhost:8001/
curl http://localhost:8003/
curl http://localhost:8004/

# Check Nginx error log
sudo tail -f /var/log/nginx/error.log

# Restart problem container
docker restart movie_catalog_service
```

### Issue 4: Port conflicts

```bash
# Check what's using port 8001
sudo netstat -tlnp | grep 8001

# If Phase 2 service still running:
sudo systemctl stop cineworld-catalog
sudo systemctl is-active cineworld-catalog
```

### Issue 5: Database connection errors

```bash
# Check DB container
docker logs movie_mysql_container

# Verify .env uses 'db' as host (not localhost):
cat .env | grep DATABASE_URL
# Should be: mysql+pymysql://user:password@db:3306/...

# Test DB connection
docker exec -it movie_mysql_container mysql -u user -p
```

### Issue 6: Images not found on Docker Hub

```bash
# Error: manifest not found
# Solution: Verify image names match exactly

docker pull your-username/cineworld-catalog:latest

# If fails, images weren't pushed
# Go back to Windows and push again
```

---

## 🔄 Rollback to Phase 2 (Nếu cần)

**Nếu Phase 3 gặp vấn đề và cần rollback:**

```bash
# Stop Docker containers
docker-compose -f docker-compose.prod.yml down

# Restore Phase 2 Nginx config
sudo cp /etc/nginx/sites-available/cineworld.phase2.backup /etc/nginx/sites-available/cineworld
sudo nginx -t
sudo systemctl reload nginx

# Restart Phase 2 services
for service in catalog otp identity booking payment redemption management scheduler; do
    sudo systemctl start cineworld-$service
    sudo systemctl enable cineworld-$service
done

# Verify
systemctl list-units --type=service --state=running | grep cineworld
```

---

## 📸 Screenshots for Documentation

**Chụp screenshots của:**

1. ✅ Docker Hub repositories (9 images)
2. ✅ `docker ps` output showing 11 containers
3. ✅ HTTPS working in browser (lock icon)
4. ✅ API Swagger docs accessible
5. ✅ Nginx config showing Docker upstreams
6. ✅ SSL certificate details (Let's Encrypt)
7. ✅ Complete booking flow working

---

## 🎯 Phase 3 Evidence Checklist

- [ ] **Docker Registry:**
  - [ ] Screenshot Docker Hub với 9 repositories
  - [ ] Screenshot image tags và sizes

- [ ] **Server Deployment:**
  - [ ] Screenshot `docker ps` on server
  - [ ] Screenshot `docker-compose.prod.yml` (image: pull from registry, NOT build)
  - [ ] Screenshot Nginx config với Docker upstream targets

- [ ] **HTTPS Testing:**
  - [ ] Screenshot browser showing HTTPS lock icon
  - [ ] Screenshot SSL certificate details
  - [ ] Screenshot API đáp ứng qua HTTPS
  - [ ] Screenshot curl output testing HTTPS

- [ ] **Functionality:**
  - [ ] Screenshot complete booking flow
  - [ ] Screenshot e-ticket received
  - [ ] Screenshot Adminer database access

- [ ] **Reliability:**
  - [ ] Screenshot restart policy: `restart: always`
  - [ ] Screenshot Docker volume for persistence
  - [ ] Video demo container auto-restart after manual stop

---

## 📚 Additional Resources

### Useful Commands

```bash
# View all logs
docker-compose -f docker-compose.prod.yml logs

# View specific service logs
docker logs -f movie_booking_service --tail 100

# Restart specific service
docker restart movie_catalog_service

# Restart all services
docker-compose -f docker-compose.prod.yml restart

# Stop all
docker-compose -f docker-compose.prod.yml down

# Stop and remove volumes (⚠️ DELETES DATA)
docker-compose -f docker-compose.prod.yml down -v

# Update to new image versions
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Check resource usage
docker stats --no-stream
```

### Backup Database

```bash
# Backup volume
docker run --rm \
  -v moviebookingsystem_mysql_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/mysql-backup-$(date +%Y%m%d).tar.gz /data

# Restore volume
docker run --rm \
  -v moviebookingsystem_mysql_data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/mysql-backup-20260320.tar.gz -C /
```

---

## 🏆 Success Criteria

✅ **Docker Hub:** 9 images published
✅ **Containers:** 11 containers running on production server
✅ **Nginx:** Updated to proxy to Docker containers
✅ **HTTPS:** Working với Let's Encrypt certificate
✅ **APIs:** All endpoints accessible qua HTTPS
✅ **Booking Flow:** Complete flow works end-to-end
✅ **Persistence:** Database survives container restarts
✅ **Auto-Restart:** Containers restart automatically on failure
✅ **Documentation:** Screenshots và video demo completed

---

**Phase 3 Deployment Complete! 🎉**

Your microservices system is now:
- **Containerized** with Docker
- **Reproducible** via docker-compose
- **Portable** across environments
- **Secure** with HTTPS via Nginx + Let's Encrypt
- **Resilient** with auto-restart policies
- **Production-ready** on AWS EC2

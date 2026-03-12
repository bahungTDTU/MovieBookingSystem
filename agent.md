# Agent Context - CineWorld Movie Booking System (DevOps Midterm)

## Thông tin dự án
- **Tên**: CineWorld - Microservices Movie Booking System
- **Đường dẫn**: `d:\DevOps\MovieBookingSystem\MovieBookingSystem`
- **Môn học**: 502094 - Software Deployment, Operations and Maintenance (Midterm)
- **Mục tiêu**: Deploy ứng dụng đặt vé xem phim lên Ubuntu cloud server theo 2 cách: Traditional (Phase 2) và Docker (Phase 3)

## Tech Stack
- **Backend**: Python 3.9 + FastAPI + Uvicorn (8 microservices)
- **Frontend**: Static HTML/CSS/JS served bởi Nginx Alpine
- **Database**: MySQL 8.0
- **ORM**: SQLAlchemy + PyMySQL
- **Containerization**: Docker + Docker Compose
- **Services**: catalog (8001), otp (8002), identity (8003), booking (8004), payment (8005), redemption (8006), management (8007), scheduler (background), frontend (3000)

## Cấu trúc thư mục hiện tại
```
MovieBookingSystem/
├── .git/                    # Git đã được khởi tạo
├── .gitignore               # ✅ Đã tạo (Python, Docker, IDE, OS)
├── README.md                # ✅ Đã có sẵn (đầy đủ)
├── agent.md                 # File context này
├── docker-compose.yml       # Docker Compose cho toàn bộ hệ thống
├── database/
│   └── init.sql             # SQL khởi tạo database
├── frontend/
│   ├── Dockerfile           # Nginx Alpine
│   ├── index.html, admin.html, booking.html, ...
│   ├── app.js, style.css
│   └── ...
├── services/
│   ├── catalog/             # Mỗi service có: Dockerfile, requirements.txt, main.py
│   ├── otp/
│   ├── identity/
│   ├── booking/
│   ├── payment/
│   ├── redemption/
│   ├── management/
│   └── scheduler/
└── scripts/
    └── setup.sh             # ✅ Đã tạo - Linux automation script
```

## Những gì đã thực hiện

### 1. Tạo file `.gitignore` ✅
- Đường dẫn: `d:\DevOps\MovieBookingSystem\MovieBookingSystem\.gitignore`
- Nội dung: Bỏ qua `__pycache__/`, `*.py[cod]`, `venv/`, `.env`, `mysql_data/`, IDE files, OS files, logs

### 2. Tạo file `scripts/setup.sh` ✅
- Đường dẫn: `d:\DevOps\MovieBookingSystem\MovieBookingSystem\scripts\setup.sh`
- **Automation script cho Ubuntu 22.04+ server** (Phase 1 requirement)
- Gồm 11 bước:
  1. System update (`apt update/upgrade`)
  2. Install build tools (curl, wget, git, gnupg...)
  3. Install Python 3 + pip + venv + dev libraries (libffi, libssl, libjpeg...)
  4. Install MySQL 8.0 server & client
  5. Install Nginx (reverse proxy)
  6. Install Certbot (Let's Encrypt SSL)
  7. Tạo cấu trúc thư mục app tại `/opt/cineworld/` (services, frontend, database, logs, uploads, config)
  8. Tạo Python virtual environment cho mỗi microservice
  9. Tạo `.env.template` (không chứa hardcoded credentials)
  10. Cấu hình UFW firewall (SSH + HTTP/HTTPS)
  11. In tóm tắt kết quả

### 3. README.md (đã có sẵn) ✅
- Mô tả đầy đủ kiến trúc microservices, hướng dẫn cài đặt, API docs, troubleshooting

## Những gì CẦN làm tiếp (theo đề midterm)

### Phase 1 - Git Workflow & Linux Automation
- [ ] Push code lên GitHub repository
- [ ] Thiết lập Branch Protection trên branch `main`:
  - Required pull requests before merging
  - At least 1 reviewer per PR
  - No direct commits to main
  - No force-push
- [ ] Tạo workflow làm việc qua Pull Requests (feature branches → PR → review → merge)
- [ ] Tạo thư mục `docs/` cho screenshots, diagrams (optional)
- [ ] Tạo cấu trúc deliverables: `phase1/`, `phase2/`, `phase3/` (theo yêu cầu Section 8)

### Phase 2 - Traditional Deployment on Ubuntu
- [ ] Provision Ubuntu server (AWS/Azure/GCP/DigitalOcean)
- [ ] Secure server (UFW, SSH config)
- [ ] Chạy `setup.sh` trên server
- [ ] Cấu hình MySQL database + import `init.sql`
- [ ] Deploy từng microservice natively (dùng systemd hoặc PM2)
- [ ] Cấu hình Nginx reverse proxy
- [ ] Mua domain + trỏ DNS
- [ ] Cài SSL certificate (Certbot)
- [ ] Test toàn bộ hệ thống qua HTTPS

### Phase 3 - Docker Deployment
- [ ] Cài Docker + Docker Compose trên server
- [ ] Build Docker images cho từng service
- [ ] Push images lên Docker Hub
- [ ] Tạo `docker-compose.yml` cho production (pull từ registry, không build local)
- [ ] Cấu hình volumes cho database persistence + uploads
- [ ] Cấu hình restart policies (`restart: always`)
- [ ] Update Nginx upstream để trỏ vào container
- [ ] Đảm bảo Docker auto-start khi server reboot
- [ ] Test HTTPS vẫn hoạt động

### Evidence & Reporting
- [ ] Thu thập screenshots cho mỗi phase
- [ ] Viết Technical Report (theo template giảng viên)
- [ ] So sánh Phase 2 vs Phase 3 (maintainability, reproducibility, resilience, complexity, security, cost)
- [ ] Chuẩn bị slide presentation
- [ ] Quay video demo

## Lưu ý quan trọng
- **docker-compose.yml hiện tại** có chứa SMTP credentials ở `otp_service` → cần di chuyển vào `.env` file trước khi commit
- Đề yêu cầu **tất cả thành viên** phải có commit history với meaningful contributions
- Phase 3 yêu cầu **pull image từ Docker Hub**, không build trực tiếp trên server
- Reverse proxy (Nginx) từ Phase 2 được **giữ lại** ở Phase 3, chỉ thay đổi upstream target

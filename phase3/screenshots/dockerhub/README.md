# Phase 3 – Docker Hub Repository Screenshots

## Purpose

This directory contains screenshots of the Docker Hub repositories showing all CineWorld
service images pushed and publicly available.

## Required Screenshots

| Filename | Content |
|----------|---------|
| `dockerhub-overview.png` | Docker Hub profile page listing all CineWorld repositories |
| `dockerhub-frontend.png` | `your-username/cineworld-frontend` repository page with tags |
| `dockerhub-catalog.png` | `your-username/cineworld-catalog` repository page with tags |
| `dockerhub-identity.png` | `your-username/cineworld-identity` repository page with tags |
| `dockerhub-booking.png` | `your-username/cineworld-booking` repository page with tags |
| `dockerhub-payment.png` | `your-username/cineworld-payment` repository page with tags |
| `dockerhub-otp.png` | `your-username/cineworld-otp` repository page with tags |
| `dockerhub-redemption.png` | `your-username/cineworld-redemption` repository page with tags |
| `dockerhub-management.png` | `your-username/cineworld-management` repository page with tags |
| `dockerhub-scheduler.png` | `your-username/cineworld-scheduler` repository page with tags |

## Expected Docker Hub Repositories

```
your-dockerhub-username/
├── cineworld-frontend      (Nginx serving static HTML/JS/CSS)
├── cineworld-catalog       (FastAPI – port 8001)
├── cineworld-otp           (FastAPI – port 8002)
├── cineworld-identity      (FastAPI – port 8003)
├── cineworld-booking       (FastAPI – port 8004)
├── cineworld-payment       (FastAPI – port 8005)
├── cineworld-redemption    (FastAPI – port 8006)
├── cineworld-management    (FastAPI – port 8007)
└── cineworld-scheduler     (Python background job)
```

Each repository should show:
- At least one tag: `latest`
- Last pushed timestamp
- Image size

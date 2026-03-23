# Phase 3 – Evidence: HTTPS Reverse Proxy Routing

## Purpose

This directory contains evidence verifying that the Nginx reverse proxy continues to route
HTTPS traffic correctly to Docker containers (identical to Phase 2 but with Docker upstreams).

## Required Screenshots

| Filename | Content |
|----------|---------|
| `nginx-config-diff.png` | Side-by-side of Phase 2 vs Phase 3 nginx config showing upstream change |
| `curl-https-homepage.png` | `curl -I https://tungtungtungtungsahur.site` showing `HTTP/2 200` |
| `curl-https-api.png` | `curl -s https://tungtungtungtungsahur.site/api/catalog/movies` returning JSON |
| `browser-padlock.png` | Browser with padlock icon showing valid certificate on the site |
| `nginx-status.png` | `systemctl status nginx` showing active |
| `certbot-valid.png` | `sudo certbot certificates` showing valid, unexpired certificate |

## Nginx Configuration (Phase 3)

The Phase 3 Nginx config (`phase3/nginx-production-docker.conf`) routes to Docker container
ports on localhost (same ports as Phase 2, but now served by Docker):

```
HTTPS 443 → /api/catalog/   → localhost:8001  (Docker: cineworld_catalog)
           → /api/otp/       → localhost:8002  (Docker: cineworld_otp)
           → /api/identity/  → localhost:8003  (Docker: cineworld_identity)
           → /api/booking/   → localhost:8004  (Docker: cineworld_booking)
           → /api/payment/   → localhost:8005  (Docker: cineworld_payment)
           → /api/redemption/→ localhost:8006  (Docker: cineworld_redemption)
           → /api/management/→ localhost:8007  (Docker: cineworld_management)
           → /               → localhost:3000  (Docker: cineworld_frontend)
```

## Verification Commands

```bash
# Test all API endpoints via HTTPS
for path in catalog otp identity booking payment redemption management; do
    echo -n "https://tungtungtungtungsahur.site/api/$path/ → "
    curl -s -o /dev/null -w "%{http_code}\n" https://tungtungtungtungsahur.site/api/$path/
done

# Full request headers (confirm HTTPS + HSTS header)
curl -I https://tungtungtungtungsahur.site

# Test certificate validity
curl --cert-status https://tungtungtungtungsahur.site

# Nginx test
sudo nginx -t
```

## Expected curl -I output

```
HTTP/2 200
server: nginx/1.xx.x
content-type: text/html; charset=utf-8
strict-transport-security: max-age=31536000; includeSubDomains
x-frame-options: SAMEORIGIN
x-content-type-options: nosniff
```

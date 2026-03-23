# Phase 2 – System Operational State Screenshots

## Purpose

This directory contains screenshots demonstrating that the deployed system is fully operational,
including all microservices running, database connectivity verified, and file upload functionality
confirmed.

## Required Screenshots

### Service Status
| Filename | Content |
|----------|---------|
| `systemctl-all-services.png` | Output of `systemctl status cineworld-*` showing all services as `active (running)` |
| `service-ports-listening.png` | Output of `ss -tlnp | grep 800` showing all 7 ports (8001–8007) listening |
| `post-reboot-all-active.png` | Services active after a full server reboot |

### Database Connectivity
| Filename | Content |
|----------|---------|
| `mysql-running.png` | Output of `systemctl status mysql` showing active |
| `mysql-tables.png` | Output of `mysql -u cineworld_user -p -e "SHOW TABLES;"` listing all DB tables |
| `api-db-health.png` | Browser/curl response from `/api/catalog/movies` returning actual data |

### File Uploads
| Filename | Content |
|----------|---------|
| `upload-success.png` | Admin panel showing a successfully uploaded movie poster image |
| `uploads-directory.png` | Terminal output of `ls -la /opt/cineworld/uploads/` showing uploaded files |
| `image-served-browser.png` | Browser displaying uploaded image via `https://tungtungtungtungsahur.site/uploads/<file>` |

### End-to-End Functionality
| Filename | Content |
|----------|---------|
| `homepage-https.png` | CineWorld homepage loaded over HTTPS |
| `booking-flow.png` | Successful movie booking process screenshot |
| `nginx-access-log.png` | Nginx access log showing real HTTP 200 requests |

## Verification Commands

```bash
# Check all services
for s in catalog otp identity booking payment redemption management scheduler; do
    echo -n "cineworld-$s: "
    systemctl is-active cineworld-$s
done

# Check listening ports
ss -tlnp | grep -E '800[1-7]'

# Check database tables
mysql -u cineworld_user -p movie_booking_db -e "SHOW TABLES;"

# Test API endpoint
curl -s https://tungtungtungtungsahur.site/api/catalog/movies | python3 -m json.tool | head -20

# List uploaded files
ls -lh /opt/cineworld/uploads/
```

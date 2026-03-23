# Phase 3 – Evidence: Persistent Volume Behaviour

## Purpose

This directory contains evidence demonstrating that Docker named volumes correctly persist
data (database records and uploaded files) across container restarts, Docker daemon restarts,
and full server reboots.

## Required Screenshots / Evidence

| Filename | Content |
|----------|---------|
| `docker-volume-ls.png` | `docker volume ls` listing `cineworld_mysql_data` and `cineworld_uploads_data` |
| `docker-volume-inspect.png` | `docker volume inspect cineworld_mysql_data` showing mountpoint |
| `data-before-restart.png` | API response / DB query showing data BEFORE container restart |
| `container-restart.png` | Terminal showing `docker compose restart` or `docker compose down && up` |
| `data-after-restart.png` | Same API response / DB query showing data is INTACT after restart |
| `reboot-data-persistence.png` | Data intact after full server reboot |

## Volumes Defined

```yaml
volumes:
  mysql_data:
    driver: local   # Stores MySQL data at /var/lib/docker/volumes/mysql_data/_data
  uploads_data:
    driver: local   # Stores uploaded files at /var/lib/docker/volumes/uploads_data/_data
```

## Persistence Test Procedure

### 1. Verify volumes exist
```bash
docker volume ls
# Expected:
# DRIVER    VOLUME NAME
# local     phase3_mysql_data
# local     phase3_uploads_data
```

### 2. Insert test data and upload a file
```bash
# Query current movies count
curl -s https://tungtungtungtungsahur.site/api/catalog/movies | python3 -m json.tool | grep total

# Upload a test image via admin panel and note the filename
```

### 3. Restart containers (WITHOUT removing volumes)
```bash
docker compose -f docker-compose.prod.yml down
# Note: do NOT use --volumes flag
docker compose -f docker-compose.prod.yml up -d
```

### 4. Verify data survived
```bash
# Same query - count should be identical
curl -s https://tungtungtungtungsahur.site/api/catalog/movies | python3 -m json.tool | grep total

# Uploaded file should still be accessible
curl -I https://tungtungtungtungsahur.site/uploads/<your-test-file>
```

### 5. Full server reboot test
```bash
sudo reboot
# After reboot:
docker ps        # All containers should be running (restart: always)
curl -s https://tungtungtungtungsahur.site/api/catalog/movies  # Data intact
```

## Volume Inspect Output (Example)

```json
[
    {
        "CreatedAt": "2025-XX-XXTXX:XX:XX",
        "Driver": "local",
        "Labels": {
            "com.docker.compose.project": "docker-compose",
            "com.docker.compose.volume": "mysql_data"
        },
        "Mountpoint": "/var/lib/docker/volumes/docker-compose_mysql_data/_data",
        "Name": "docker-compose_mysql_data",
        "Options": null,
        "Scope": "local"
    }
]
```

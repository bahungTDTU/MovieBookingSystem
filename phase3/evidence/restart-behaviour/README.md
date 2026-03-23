# Phase 3 – Evidence: Container Restart Behaviour

## Purpose

This directory contains evidence demonstrating that the CineWorld containerised system
restarts correctly after three scenarios:
1. Individual container restarts
2. Docker daemon restarts
3. Full server reboots

## Required Screenshots

### Scenario 1 – Container Restart
| Filename | Content |
|----------|---------|
| `container-restart-command.png` | `docker restart movie_catalog_service` command |
| `container-restart-recovery.png` | `docker ps` showing container back as `Up` within seconds |

### Scenario 2 – Docker Daemon Restart
| Filename | Content |
|----------|---------|
| `daemon-restart-command.png` | `sudo systemctl restart docker` command |
| `daemon-restart-containers-up.png` | `docker ps` showing ALL containers auto-started after daemon restart |

### Scenario 3 – Full Server Reboot
| Filename | Content |
|----------|---------|
| `reboot-command.png` | `sudo reboot` command |
| `post-reboot-docker-ps.png` | `docker ps` after reboot showing all containers running |
| `post-reboot-api-test.png` | `curl https://tungtungtungtungsahur.site/api/catalog/movies` returning data after reboot |

## Test Procedure

### Scenario 1 – Individual Container Restart

```bash
# Stop and verify the container exits
docker stop movie_catalog_service
docker ps  # movie_catalog_service should NOT appear

# Wait 5-10 seconds for restart: always policy to kick in
sleep 10
docker ps  # movie_catalog_service should re-appear as "Up X seconds"
```

### Scenario 2 – Docker Daemon Restart

```bash
# Restart the Docker service
sudo systemctl restart docker

# Wait for containers to come back up
sleep 15

# Verify all containers are running
docker ps
# All containers with restart: always should be Up
```

### Scenario 3 – Full Server Reboot

```bash
# Reboot the server
sudo reboot

# After SSH reconnection (~60-90 seconds):
docker ps
# All containers should be Up

# Verify the application is working end-to-end
curl -I https://tungtungtungtungsahur.site
curl -s https://tungtungtungtungsahur.site/api/catalog/movies | python3 -m json.tool | head -5
```

## Why Containers Auto-Restart

All services in `docker-compose.prod.yml` have `restart: always`:
```yaml
catalog_service:
  restart: always
```

This policy means:
- Container restarts immediately if it exits for any reason
- Container restarts when the Docker daemon starts (including after server reboot)
- Docker daemon itself is enabled as a systemd service: `sudo systemctl enable docker`

## Docker Daemon Auto-Start Verification

```bash
# Verify Docker is enabled on boot
sudo systemctl is-enabled docker
# Expected output: enabled

# Check Docker daemon status
sudo systemctl status docker
```

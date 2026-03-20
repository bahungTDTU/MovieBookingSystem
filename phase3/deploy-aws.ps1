# 🚀 AWS EC2 Deployment Script - Phase 3

# =============================================================================
# This script automates Phase 3 deployment to AWS EC2
# Server: 13.219.51.85
# Domain: tungtungtungtungsahur.site
# =============================================================================

Write-Host "=== Phase 3 - AWS EC2 Deployment Script ===" -ForegroundColor Cyan
Write-Host ""

$SERVER_IP = "13.219.51.85"
$SERVER_USER = "ubuntu"
$SSH_KEY = "C:\Users\Nguyen Long\.ssh\cineworld-key1.pem"
$DOMAIN = "tungtungtungtungsahur.site"
$PROJECT_DIR = "C:\Users\Nguyen Long\Downloads\MovieBookingSystem (2)"

Write-Host "[INFO] Server IP: $SERVER_IP" -ForegroundColor Yellow
Write-Host "[INFO] Domain: $DOMAIN" -ForegroundColor Yellow
Write-Host "[INFO] SSH Key: $SSH_KEY" -ForegroundColor Yellow
Write-Host ""

# =============================================================================
# PHASE 1: Check Prerequisites
# =============================================================================
Write-Host "=== PHASE 1: Checking Prerequisites ===" -ForegroundColor Green
Write-Host ""

# Check Docker
Write-Host "[1/3] Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "[OK] Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker not found. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check Docker Hub login
Write-Host "[2/3] Checking Docker Hub login..." -ForegroundColor Yellow
$dockerInfo = docker info 2>&1 | Select-String "Username"
if ($dockerInfo) {
    Write-Host "[OK] Docker Hub logged in" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Not logged into Docker Hub. Please run 'docker login'" -ForegroundColor Red
    docker login
}

# Check SSH key exists
Write-Host "[3/3] Checking SSH key..." -ForegroundColor Yellow
if (Test-Path $SSH_KEY) {
    Write-Host "[OK] SSH key found" -ForegroundColor Green
} else {
    Write-Host "[ERROR] SSH key not found at: $SSH_KEY" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[OK] All prerequisites met!" -ForegroundColor Green
Write-Host ""

# =============================================================================
# Ask for Docker Hub username
# =============================================================================
$USERNAME = Read-Host "Enter your Docker Hub username"
if ([string]::IsNullOrWhiteSpace($USERNAME)) {
    Write-Host "[ERROR] Docker Hub username required!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[INFO] Docker Hub username: $USERNAME" -ForegroundColor Cyan
Write-Host ""

# =============================================================================
# PHASE 2: Tag and Push Images to Docker Hub
# =============================================================================
Write-Host "=== PHASE 2: Pushing Images to Docker Hub ===" -ForegroundColor Green
Write-Host ""

$images = @(
    "catalog_service",
    "identity_service",
    "otp_service",
    "booking_service",
    "payment_service",
    "redemption_service",
    "management_service",
    "scheduler_service",
    "frontend"
)

$totalImages = $images.Count
$current = 0

foreach ($image in $images) {
    $current++
    $localImage = "moviebookingsystem2-$image"
    $hubImage = "$USERNAME/cineworld-$($image.Replace('_service','')):latest"

    Write-Host "[$current/$totalImages] Processing $image..." -ForegroundColor Yellow

    # Tag
    Write-Host "  Tagging: $localImage -> $hubImage" -ForegroundColor White
    docker tag $localImage $hubImage

    # Push
    Write-Host "  Pushing to Docker Hub..." -ForegroundColor White
    docker push $hubImage

    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] $image pushed successfully" -ForegroundColor Green
    } else {
        Write-Host "  [ERROR] Failed to push $image" -ForegroundColor Red
        exit 1
    }
    Write-Host ""
}

Write-Host "[OK] All images pushed to Docker Hub!" -ForegroundColor Green
Write-Host "[INFO] Verify at: https://hub.docker.com/u/$USERNAME" -ForegroundColor Cyan
Write-Host ""

# =============================================================================
# PHASE 3: Update docker-compose.prod.yml
# =============================================================================
Write-Host "=== PHASE 3: Updating docker-compose.prod.yml ===" -ForegroundColor Green
Write-Host ""

$composeFile = Join-Path $PROJECT_DIR "docker-compose.prod.yml"

# Read and replace username
$content = Get-Content $composeFile -Raw
$content = $content -replace "your-dockerhub-username", $USERNAME

# Save
Set-Content -Path $composeFile -Value $content

Write-Host "[OK] docker-compose.prod.yml updated with username: $USERNAME" -ForegroundColor Green
Write-Host ""

# =============================================================================
# PHASE 4: Upload Files to Server
# =============================================================================
Write-Host "=== PHASE 4: Uploading Files to AWS EC2 ===" -ForegroundColor Green
Write-Host ""

$filesToUpload = @(
    "docker-compose.prod.yml",
    ".env",
    "phase3\nginx-production-docker.conf"
)

foreach ($file in $filesToUpload) {
    $filePath = Join-Path $PROJECT_DIR $file
    Write-Host "[UPLOAD] $file" -ForegroundColor Yellow

    scp -i $SSH_KEY $filePath "${SERVER_USER}@${SERVER_IP}:/home/ubuntu/"

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] $file uploaded" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Failed to upload $file" -ForegroundColor Red
        exit 1
    }
}

# Upload database folder
Write-Host "[UPLOAD] database folder" -ForegroundColor Yellow
$dbPath = Join-Path $PROJECT_DIR "database"
scp -i $SSH_KEY -r $dbPath "${SERVER_USER}@${SERVER_IP}:/home/ubuntu/"

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] database folder uploaded" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Failed to upload database folder" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[OK] All files uploaded successfully!" -ForegroundColor Green
Write-Host ""

# =============================================================================
# PHASE 5: Deploy on Server
# =============================================================================
Write-Host "=== PHASE 5: Deploying on AWS EC2 Server ===" -ForegroundColor Green
Write-Host ""

Write-Host "[INFO] Now SSH into the server and run the following commands:" -ForegroundColor Cyan
Write-Host ""

$deployScript = @"
# =============================================================================
# Run these commands on the server (after SSH)
# =============================================================================

# 1. Stop Phase 2 services
for s in catalog otp identity booking payment redemption management scheduler; do
    sudo systemctl stop cineworld-`$s
    sudo systemctl disable cineworld-`$s
done

# 2. Verify stopped
systemctl list-units | grep cineworld | grep running

# 3. Backup and update Nginx
sudo cp /etc/nginx/sites-available/cineworld /etc/nginx/sites-available/cineworld.phase2.backup
sudo cp /home/ubuntu/nginx-production-docker.conf /etc/nginx/sites-available/cineworld
sudo sed -i 's/YOUR_DOMAIN/$DOMAIN/g' /etc/nginx/sites-available/cineworld

# 4. Test and reload Nginx
sudo nginx -t
sudo systemctl reload nginx

# 5. Install Docker (if needed)
docker --version || {
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker ubuntu
    newgrp docker
    sudo systemctl enable docker
}

# 6. Pull and start containers
cd /home/ubuntu
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# 7. Wait and verify
sleep 30
docker ps

# 8. Test HTTPS
curl -I https://$DOMAIN
curl -k https://$SERVER_IP/api/catalog/movies

echo ""
echo "=== Deployment Complete! ==="
echo "Access at: https://$DOMAIN"
echo "Or: https://$SERVER_IP"
"@

Write-Host $deployScript -ForegroundColor White
Write-Host ""

# Save script to file
$serverScriptPath = Join-Path $PROJECT_DIR "phase3\deploy-to-aws.sh"
$deployScript | Out-File -FilePath $serverScriptPath -Encoding UTF8

Write-Host "[OK] Server deployment script saved to: phase3\deploy-to-aws.sh" -ForegroundColor Green
Write-Host ""

# =============================================================================
# Final Instructions
# =============================================================================
Write-Host "=== Next Steps ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. SSH into the server:" -ForegroundColor White
Write-Host "   ssh -i `"$SSH_KEY`" $SERVER_USER@$SERVER_IP" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Run the deployment commands (see above) or:" -ForegroundColor White
Write-Host "   bash ~/deploy-to-aws.sh" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Test HTTPS:" -ForegroundColor White
Write-Host "   https://$DOMAIN" -ForegroundColor Yellow
Write-Host "   https://$SERVER_IP" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. Test APIs:" -ForegroundColor White
Write-Host "   https://$DOMAIN/api/catalog/docs" -ForegroundColor Yellow
Write-Host ""

Write-Host "=== Deployment Ready! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Press Enter to open SSH connection..." -ForegroundColor Cyan
$null = Read-Host

# Open SSH
ssh -i $SSH_KEY "$SERVER_USER@$SERVER_IP"

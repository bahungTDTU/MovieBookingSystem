# =============================================================================
# Generate Self-Signed SSL Certificate for Local HTTPS Testing
# =============================================================================
# This script creates a self-signed certificate for localhost
# WARNING: Self-signed certificates will show browser security warnings
# For production, use Let's Encrypt instead
# =============================================================================

Write-Host "=== Generating Self-Signed SSL Certificate ===" -ForegroundColor Cyan
Write-Host ""

# Create SSL directory
$sslDir = "$PSScriptRoot\ssl"
if (-not (Test-Path $sslDir)) {
    New-Item -ItemType Directory -Path $sslDir | Out-Null
    Write-Host "[OK] Created SSL directory: $sslDir" -ForegroundColor Green
}

# Generate certificate using OpenSSL (requires OpenSSL to be installed)
# Alternative: Use PowerShell's New-SelfSignedCertificate

Write-Host ""
Write-Host "Checking for OpenSSL..." -ForegroundColor Yellow

$opensslPath = Get-Command openssl -ErrorAction SilentlyContinue

if ($opensslPath) {
    Write-Host "[OK] OpenSSL found: $($opensslPath.Source)" -ForegroundColor Green
    Write-Host ""
    Write-Host "Generating certificate with OpenSSL..." -ForegroundColor Yellow

    # Generate private key and certificate
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 `
        -keyout "$sslDir\localhost.key" `
        -out "$sslDir\localhost.crt" `
        -subj "/C=VN/ST=HoChiMinh/L=HoChiMinh/O=CineWorld/OU=Development/CN=localhost"

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "[OK] SSL Certificate generated successfully!" -ForegroundColor Green
        Write-Host "[OK] Certificate: $sslDir\localhost.crt" -ForegroundColor Green
        Write-Host "[OK] Private Key: $sslDir\localhost.key" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Failed to generate certificate with OpenSSL" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[WARNING] OpenSSL not found. Using PowerShell method..." -ForegroundColor Yellow
    Write-Host ""

    # Use PowerShell's New-SelfSignedCertificate (Windows 10+)
    try {
        $cert = New-SelfSignedCertificate `
            -DnsName "localhost" `
            -CertStoreLocation "Cert:\CurrentUser\My" `
            -KeyUsage DigitalSignature,KeyEncipherment `
            -KeyAlgorithm RSA `
            -KeyLength 2048 `
            -NotAfter (Get-Date).AddYears(1) `
            -Subject "CN=localhost"

        # Export certificate
        $certPath = "$sslDir\localhost.crt"
        $keyPath = "$sslDir\localhost.key"

        # Export as PFX first
        $pfxPath = "$sslDir\localhost.pfx"
        $password = ConvertTo-SecureString -String "temp" -Force -AsPlainText
        Export-PfxCertificate -Cert $cert -FilePath $pfxPath -Password $password | Out-Null

        # Convert PFX to PEM format (requires OpenSSL or manual conversion)
        Write-Host "[OK] Certificate created in Windows Certificate Store" -ForegroundColor Green
        Write-Host "[OK] PFX file: $pfxPath" -ForegroundColor Green
        Write-Host ""
        Write-Host "[INFO] To use with Nginx, you need to convert PFX to PEM format" -ForegroundColor Yellow
        Write-Host "[INFO] Install OpenSSL and run:" -ForegroundColor Yellow
        Write-Host "  openssl pkcs12 -in $pfxPath -out $certPath -nodes -nokeys" -ForegroundColor White
        Write-Host "  openssl pkcs12 -in $pfxPath -out $keyPath -nodes -nocerts" -ForegroundColor White

    } catch {
        Write-Host "[ERROR] Failed to generate certificate: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "=== Certificate Details ===" -ForegroundColor Cyan
Write-Host "Certificate: localhost.crt" -ForegroundColor White
Write-Host "Private Key: localhost.key" -ForegroundColor White
Write-Host "Valid for: 365 days" -ForegroundColor White
Write-Host ""
Write-Host "[WARNING] This is a self-signed certificate. Browsers will show security warnings." -ForegroundColor Yellow
Write-Host "[INFO] Click 'Advanced' -> 'Proceed to localhost (unsafe)' to access the site." -ForegroundColor Yellow
Write-Host ""
Write-Host "=== Next Steps ===" -ForegroundColor Cyan
Write-Host "1. Install Nginx on Windows or use Nginx Docker container" -ForegroundColor White
Write-Host "2. Copy nginx-https-local.conf to Nginx config directory" -ForegroundColor White
Write-Host "3. Update SSL certificate paths in the config" -ForegroundColor White
Write-Host "4. Restart Nginx" -ForegroundColor White
Write-Host "5. Access https://localhost" -ForegroundColor White

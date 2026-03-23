# Phase 2 – HTTPS Certificate Installation Evidence

## Purpose

This directory contains screenshots and logs demonstrating that a valid TLS certificate has been
obtained from Let's Encrypt via Certbot and that HTTPS is active on the server.

## Required Screenshots

| Filename | Content |
|----------|---------|
| `certbot-install-output.png` | Terminal output of `sudo certbot --nginx -d tungtungtungtungsahur.site` |
| `certbot-certificates.png` | Output of `sudo certbot certificates` showing certificate details |
| `nginx-ssl-test.png` | Output of `sudo nginx -t` confirming valid SSL configuration |
| `https-browser.png` | Browser screenshot showing the padlock icon and valid certificate on `https://tungtungtungtungsahur.site` |
| `curl-https.png` | Terminal output of `curl -I https://tungtungtungtungsahur.site` showing `HTTP/2 200` |

## Certbot SSL Installation

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate (Certbot auto-configures Nginx)
sudo certbot --nginx -d tungtungtungtungsahur.site -d www.tungtungtungtungsahur.site \
    --non-interactive --agree-tos --email your-email@example.com

# Verify certificate
sudo certbot certificates
```

Expected `certbot certificates` output:
```
Found the following certs:
  Certificate Name: tungtungtungtungsahur.site
    Serial Number: ...
    Key Type: RSA
    Domains: tungtungtungtungsahur.site www.tungtungtungtungsahur.site
    Expiry Date: YYYY-MM-DD HH:MM:SS+00:00 (VALID: 89 days)
    Certificate Path: /etc/letsencrypt/live/tungtungtungtungsahur.site/fullchain.pem
    Private Key Path: /etc/letsencrypt/live/tungtungtungtungsahur.site/privkey.pem
```

## Auto-Renewal

Certbot installs a cron job / systemd timer for automatic renewal:
```bash
# Verify renewal timer
sudo systemctl status certbot.timer

# Test renewal (dry run)
sudo certbot renew --dry-run
```

## Certificate File Locations

```
/etc/letsencrypt/live/tungtungtungtungsahur.site/
├── fullchain.pem    # Certificate + intermediate chain
├── privkey.pem      # Private key
├── cert.pem         # Certificate only
└── chain.pem        # Intermediate chain only
```

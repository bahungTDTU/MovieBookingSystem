# Phase 2 – DNS Configuration Screenshots

## Purpose

This directory contains screenshots demonstrating that the DNS A record has been configured to
point the domain name to the Ubuntu cloud server's public IP address.

## Required Screenshots

Place the following screenshot files in this directory:

| Filename | Content |
|----------|---------|
| `dns-a-record.png` | DNS provider dashboard showing A record: `@ → <server-ip>` |
| `dns-propagation.png` | DNS propagation check (e.g. from https://dnschecker.org) showing global resolution |
| `nslookup-result.png` | Terminal output of `nslookup tungtungtungtungsahur.site` confirming correct IP |

## How to Capture

### 1. DNS Provider Dashboard
Log in to your DNS provider (Namecheap / GoDaddy / Cloudflare / Route 53) and take a
screenshot of the DNS records page showing:
```
Type: A
Host: @
Value: <your-server-public-ip>
TTL: 300 (or Auto)
```

### 2. DNS Propagation Check
Visit https://dnschecker.org, enter your domain, and take a screenshot showing green checkmarks
across multiple global DNS servers.

### 3. nslookup Verification
```bash
nslookup tungtungtungtungsahur.site
# Expected output:
# Server:   8.8.8.8
# Address:  8.8.8.8#53
# Non-authoritative answer:
# Name:    tungtungtungtungsahur.site
# Address: <your-server-ip>
```

## DNS Record Configuration

```
Type    Name    Value                TTL
A       @       <server-public-ip>   300
CNAME   www     tungtungtungtungsahur.site      300
```

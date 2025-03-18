# ActuClaim Server Setup Documentation

## Server Information
- **Server IP:** 178.128.237.195
- **Domain:** actuclaim.com
- **Server Provider:** Digital Ocean
- **Operating System:** Ubuntu 24.10
- **Web Server:** Nginx 1.26.0
- **Application Server:** Gunicorn
- **Python Version:** 3.12

[... rest of the previous documentation ...]

## Security Notes
- ✅ The application now runs as a dedicated non-root user (actuclaim)
- ✅ Files are located in /var/www/actuclaim instead of /root
- ✅ Proper permissions and ownership have been set for security
- ✅ SSL Certificate Implemented
  - **Provider:** Let's Encrypt
  - **Domains Secured:** 
    - actuclaim.com
    - www.actuclaim.com
  - **Certificate Location:** `/etc/letsencrypt/live/actuclaim.com/`
  - **Expiration Date:** 2025-06-16
  - **Renewal:** Automatic background task configured via Certbot
- Additional security recommendations:
  - Implementing proper firewall rules
  - Setting up regular backups of important data files

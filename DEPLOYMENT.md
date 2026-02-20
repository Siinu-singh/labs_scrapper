# Deployment Guide

## Local Development

```bash
cd scrapper_api
./run.sh
```

Access at: http://localhost:8000

---

## Production Deployment Options

### Option 1: Direct Server Deployment

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install python3 python3-pip chromium-browser chromium-chromedriver

# Clone/copy project
cd scrapper_api

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Set ENVIRONMENT=production

# Install Gunicorn
pip install gunicorn

# Run with Gunicorn (4 workers)
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Option 2: Docker Deployment

```bash
# Build image
docker build -t lab-scraper-api:latest .

# Run container
docker run -d \
  --name lab-scraper \
  -p 8000:8000 \
  --restart unless-stopped \
  lab-scraper-api:latest

# View logs
docker logs -f lab-scraper
```

### Option 3: Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
```

Run:
```bash
docker-compose up -d
```

---

## Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Systemd Service

Create `/etc/systemd/system/lab-scraper.service`:

```ini
[Unit]
Description=Lab Test Scraper API
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/scrapper_api
Environment="PATH=/path/to/scrapper_api/venv/bin"
ExecStart=/path/to/scrapper_api/venv/bin/gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable lab-scraper
sudo systemctl start lab-scraper
sudo systemctl status lab-scraper
```

---

## Cloud Deployment

### AWS EC2

1. Launch Ubuntu instance
2. Install dependencies
3. Clone project
4. Setup as systemd service
5. Configure security group (port 8000)

### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/lab-scraper
gcloud run deploy lab-scraper --image gcr.io/PROJECT_ID/lab-scraper --platform managed
```

### Heroku

Create `Procfile`:
```
web: uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

Deploy:
```bash
heroku create lab-scraper-api
git push heroku main
```

### DigitalOcean App Platform

1. Connect GitHub repo
2. Select Python
3. Set build command: `pip install -r requirements.txt`
4. Set run command: `uvicorn src.main:app --host 0.0.0.0 --port 8080`

---

## Environment Variables

Production `.env`:
```env
ENVIRONMENT=production
CHROME_BINARY_LOCATION=/usr/bin/chromium-browser
CHROMEDRIVER_PATH=/usr/bin/chromedriver
```

---

## Monitoring

### Health Check Endpoint

```bash
curl http://your-domain.com/health
```

### Uptime Monitoring

Use services like:
- UptimeRobot
- Pingdom
- StatusCake

Configure to check `/health` endpoint every 5 minutes.

---

## Performance Tuning

### Gunicorn Workers

```bash
# Formula: (2 x CPU cores) + 1
gunicorn src.main:app -w 9 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Timeout Settings

```bash
gunicorn src.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --graceful-timeout 30
```

---

## Security Checklist

- [ ] Set ENVIRONMENT=production
- [ ] Configure firewall (only port 80/443)
- [ ] Use HTTPS (Let's Encrypt)
- [ ] Set up rate limiting
- [ ] Enable CORS only for trusted domains
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity

---

## Backup & Recovery

### Backup Script

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf backup_$DATE.tar.gz scrapper_api/
```

### Recovery

```bash
tar -xzf backup_YYYYMMDD_HHMMSS.tar.gz
cd scrapper_api
./run.sh
```

---

## Troubleshooting

### Chrome/Chromium Issues

```bash
# Install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f
```

### Memory Issues

Increase worker timeout or reduce workers:
```bash
gunicorn src.main:app -w 2 --timeout 180
```

### Port Already in Use

```bash
# Find process
sudo lsof -i :8000
# Kill process
sudo kill -9 PID
```

---

## Scaling

### Horizontal Scaling

Use load balancer (Nginx/HAProxy) with multiple instances:

```nginx
upstream lab_scraper {
    server 10.0.0.1:8000;
    server 10.0.0.2:8000;
    server 10.0.0.3:8000;
}

server {
    location / {
        proxy_pass http://lab_scraper;
    }
}
```

### Vertical Scaling

Increase server resources and workers:
```bash
gunicorn src.main:app -w 16 -k uvicorn.workers.UvicornWorker
```

---

## Maintenance

### Update Dependencies

```bash
pip install --upgrade -r requirements.txt
```

### Restart Service

```bash
# Systemd
sudo systemctl restart lab-scraper

# Docker
docker restart lab-scraper

# Gunicorn
pkill gunicorn && gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

## Support

For issues, check:
1. Logs: `docker logs lab-scraper` or `/var/log/lab-scraper.log`
2. Health endpoint: `curl http://localhost:8000/health`
3. Chrome/Chromium installation
4. Port availability

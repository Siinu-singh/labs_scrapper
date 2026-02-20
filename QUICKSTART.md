# Quick Start Guide

## Installation & Setup

```bash
cd scrapper_api

# Option 1: Use the run script (recommended)
./run.sh

# Option 2: Manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Test the API

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Scrape 1mg
```bash
curl -X POST "http://localhost:8000/api/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{"test_name": "CBC", "lab_name": "1mg"}'
```

### 3. Scrape Orange Health
```bash
curl -X POST "http://localhost:8000/api/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{"test_name": "Lipid Profile", "lab_name": "orange"}'
```

### 4. Scrape Redcliffe
```bash
curl -X POST "http://localhost:8000/api/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{"test_name": "Thyroid", "lab_name": "redcliffe"}'
```

### 5. Scrape Lal Path Labs
```bash
curl -X POST "http://localhost:8000/api/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{"test_name": "KFT", "lab_name": "lalpathlabs"}'
```

## API Documentation

Visit http://localhost:8000/docs for interactive API documentation (Swagger UI)

## Docker Deployment

```bash
# Build image
docker build -t lab-scraper-api .

# Run container
docker run -p 8000:8000 lab-scraper-api
```

## Production Deployment

```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Environment Variables

Edit `.env` file:
```env
ENVIRONMENT=production  # Hide docs in production
CHROME_BINARY_LOCATION=/usr/bin/chromium-browser
CHROMEDRIVER_PATH=/usr/bin/chromedriver
```

## Troubleshooting

### Chrome/Chromium not found
```bash
sudo apt-get install chromium-browser chromium-chromedriver
```

### Port already in use
```bash
# Change port in run command
uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

### Import errors
```bash
# Make sure you're in the scrapper_api directory
cd scrapper_api
# Activate virtual environment
source venv/bin/activate
```

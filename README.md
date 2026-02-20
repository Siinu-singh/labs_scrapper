# Lab Test Scraper API

Production-ready FastAPI service for scraping lab test prices from multiple providers.

## Features

- Scrape test prices from 4 major lab providers:
  - 1mg
  - Orange Health
  - Redcliffe Labs
  - Lal Path Labs
- RESTful API with FastAPI
- Async/await for better performance
- Pydantic validation
- Production-ready structure

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Install Chrome/Chromium
sudo apt-get install chromium-browser chromium-chromedriver
```

## Run

```bash
# Development
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Health CheckCystatin C
```bash
GET /health
```

### Scrape Test Prices
```bash
POST /api/v1/scrape
Content-Type: application/json

{
  "test_name": "CBC",
  "lab_name": "1mg"
}
```

**Response:**
```json
{
  "lab": "1mg",
  "test_searched": "CBC",
  "results": [
    {
      "test_name": "Complete Blood Count (CBC)",
      "price": "₹299"
    }
  ],
  "count": 1
}
```

### Supported Labs
- `1mg`
- `orange`
- `redcliffe`
- `lalpathlabs`

## API Documentation

When running in development mode, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Example Requests

```bash
# 1mg
curl -X POST "http://localhost:8000/api/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{"test_name": "CBC", "lab_name": "1mg"}'

# Orange Health
curl -X POST "http://localhost:8000/api/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{"test_name": "Lipid Profile", "lab_name": "orange"}'

# Redcliffe
curl -X POST "http://localhost:8000/api/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{"test_name": "Thyroid", "lab_name": "redcliffe"}'

# Lal Path Labs
curl -X POST "http://localhost:8000/api/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{"test_name": "KFT", "lab_name": "lalpathlabs"}'
```

## Project Structure

```
scrapper_api/
├── src/
│   ├── scrapers/
│   │   ├── utils/
│   │   │   ├── onemg_scraper.py
│   │   │   ├── orange_scraper.py
│   │   │   ├── redcliffe_scraper.py
│   │   │   └── lalpathlabs_scraper.py
│   │   ├── router.py
│   │   ├── schemas.py
│   │   └── service.py
│   ├── config.py
│   ├── exceptions.py
│   └── main.py
├── tests/
├── requirements.txt
└── README.md
```

## Architecture

- **Router Layer**: Handles HTTP requests/responses
- **Service Layer**: Business logic and orchestration
- **Utils Layer**: Individual scraper implementations
- **Schemas**: Pydantic models for validation
- **Config**: Centralized configuration management

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid lab name or test name)
- `500`: Server error (scraping failed)

## Performance

- Async/await for non-blocking I/O
- Selenium runs in thread pool
- Headless browser for better performance
- Connection pooling

## License

MIT

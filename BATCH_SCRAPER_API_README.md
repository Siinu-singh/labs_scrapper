# Batch Scraper API Documentation

Production-ready API for scraping lab test prices across all 4 providers in a batch-wise manner.

## Quick Start

### 1. Start the Server

```bash
cd /path/to/scrapper_api
source venv/bin/activate
python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Server will be available at: `http://localhost:8000`

### 2. Open Postman

1. Open Postman desktop app
2. **Click** → Import → Upload Files
3. Select: `Batch_Scraper_API.postman_collection.json`
4. Collection loaded! You're ready to go.

### 3. Set Base URL (Optional)

In Postman:
- **Click** → Batch Scraper API collection
- **Variables** tab
- Set `base_url` to `http://localhost:8000` (default)

---

## API Endpoints

### 1. **Health Check** ✅
- **Endpoint:** `GET /health`
- **Purpose:** Verify API server is running
- **Response:** `{"status": "healthy", "version": "1.0.0"}`

### 2. **Start Batch Scraping** 🚀
- **Endpoint:** `POST /api/v1/batch/start`
- **Headers:** `Content-Type: application/json`
- **Body:**
```json
{
  "total_batches": null,
  "batch_size": 10
}
```

**Parameters:**
- `total_batches`: (Optional) Number of batches to run. `null` = all 103 tests
- `batch_size`: (1-50) Tests per batch. Default: 10

**Response:** `202 Accepted`
```json
{
  "success": true,
  "message": "Batch scraping started in background",
  "batch_size": 10,
  "total_batches": 11,
  "total_tests": 103
}
```

**Processing:**
- Scraping runs in **background** (non-blocking)
- API remains responsive
- Server handles multiple requests while scraping

### 3. **Get Batch Status** 📊
- **Endpoint:** `GET /api/v1/batch/status`
- **Purpose:** Monitor progress in real-time
- **Response:** `200 OK`

```json
{
  "status": "running",
  "current_batch": 3,
  "total_batches": 11,
  "completed_batches": 2,
  "progress_percent": 18.18,
  "batch_size": 10,
  "started_at": "2026-02-20T15:30:00.123456",
  "batches": {
    "1": {
      "status": "completed",
      "completed_at": "2026-02-20T15:32:00.123456",
      "results": {
        "batch": 1,
        "success": true,
        "total_tests": 10,
        "successful": 34,
        "failed": 6,
        "success_rate": 85.0,
        "saved_count": 34,
        "duration_seconds": 129.5
      }
    }
  }
}
```

**Status Values:**
- `idle` - No scraping in progress
- `running` - Batch scraping active
- `completed` - All batches finished

### 4. **Reset Batch State** 🔄
- **Endpoint:** `POST /api/v1/batch/reset`
- **Body:**
```json
{
  "force": false
}
```

**Parameters:**
- `force`: `false` = prevent reset if running (safe)
- `force`: `true` = force reset regardless

---

## Usage Examples

### Example 1: Scrape All 103 Tests

```
1. POST /api/v1/batch/start
   {
     "total_batches": null,
     "batch_size": 10
   }

2. GET /api/v1/batch/status  (poll every 60 seconds)

3. Wait for: status = "completed" and progress_percent = 100
   Total time: ~23 minutes
```

### Example 2: Test with Single Batch

```
1. POST /api/v1/batch/start
   {
     "total_batches": 1,
     "batch_size": 10
   }

2. GET /api/v1/batch/status (poll every 30 seconds)

3. Batch completes in ~2-3 minutes
```

### Example 3: Custom Batch Size

```
1. POST /api/v1/batch/start
   {
     "total_batches": null,
     "batch_size": 15
   }

2. Result:
   - 103 tests ÷ 15 = 7 batches
   - Each batch: ~2.5 minutes
   - Total: ~17.5 minutes
```

### Example 4: Resume After Interruption

```
1. If interrupted:
   POST /api/v1/batch/reset { "force": true }

2. Start again:
   POST /api/v1/batch/start { ... }
   
3. API automatically skips completed batches
   Resumes from next pending batch
```

---

## How It Works

### Architecture

```
┌─────────────┐
│  Postman    │
└──────┬──────┘
       │ POST /api/v1/batch/start
       ▼
┌─────────────────────────┐
│  API Server             │
│  (FastAPI - Port 8000)  │
└──────┬──────────────────┘
       │
       ├─ Response: 202 Accepted (immediate)
       │
       └─ Background Task:
          │
          ├─ Batch 1 (tests 1-10)
          │  ├─ Test 1 scraping from 4 labs
          │  ├─ Test 2 scraping from 4 labs
          │  └─ ...
          │  └─ Save to database
          │
          ├─ Batch 2 (tests 11-20)
          │  └─ ...
          │
          └─ Batch 11 (tests 101-103)
             └─ ...

Meanwhile, User can:
  ├─ Monitor with GET /api/v1/batch/status
  ├─ Fetch other data
  └─ Access other APIs
```

### Processing Details

**Per Batch:**
1. Load 10 tests from database
2. For each test:
   - Scrape from 4 labs concurrently
   - Extract price + test name
   - Parse currency symbols
3. Save successful results to `test_prices` table
4. Mark with `is_latest = 1` (for freshness tracking)
5. Record batch completion in `batch_state.json`

**Error Handling:**
- If a lab fails → skip it, continue with other labs
- If a batch fails → log error, mark as failed, continue to next batch
- No interruption to overall process

---

## Monitoring & Logging

### 1. Real-time Progress Monitoring

Use the status endpoint to track:
```bash
while true; do
  curl http://localhost:8000/api/v1/batch/status
  sleep 60  # Check every minute
done
```

### 2. Log Files

Check these files for detailed logs:
```
logs/
├── batch_scraper.log    # Batch scraping operations
├── app.log              # API operations
└── ...
```

### 3. Database Verification

```sql
-- Check latest prices
SELECT COUNT(*) FROM test_prices WHERE is_latest = 1;

-- Check by lab
SELECT lab_name, COUNT(*) as count 
FROM test_prices 
WHERE is_latest = 1 
GROUP BY lab_name;

-- Check when last updated
SELECT MAX(scraped_at) as last_update FROM test_prices;
```

---

## State Management

### Batch State File

Location: `batch_state.json`

Content example:
```json
{
  "last_completed_batch": 2,
  "total_batches": 11,
  "batch_size": 10,
  "status": "running",
  "current_batch": 3,
  "started_at": "2026-02-20T15:30:00.123456",
  "batches": {
    "1": {
      "status": "completed",
      "completed_at": "2026-02-20T15:32:00",
      "results": { ... }
    },
    "2": {
      "status": "completed",
      "completed_at": "2026-02-20T15:34:00",
      "results": { ... }
    },
    "3": {
      "status": "pending",
      "completed_at": null,
      "results": null
    }
  }
}
```

### Features

- **Persistent tracking:** State survives server restarts
- **Resume capability:** Continues from last completed batch
- **Progress history:** Records each batch's results

---

## Production Deployment

### Cron Job (Automated Scraping)

```bash
# Run daily at 2 AM
0 2 * * * curl -X POST http://localhost:8000/api/v1/batch/start \
  -H "Content-Type: application/json" \
  -d '{"total_batches": null, "batch_size": 10}' \
  >> /var/log/scraper.log 2>&1

# Weekly report
0 4 * * 1 curl -X GET http://localhost:8000/api/v1/batch/status \
  >> /var/log/scraper_status.log 2>&1
```

### Docker Deployment

```dockerfile
# In Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python3", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

```bash
# .env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/dbname
ENVIRONMENT=production
LOG_LEVEL=INFO
```

---

## Troubleshooting

### Q: API returns 500 error
**A:** Check server logs:
```bash
tail -f logs/app.log
```

### Q: Batch stuck on "running"
**A:** Reset state:
```bash
curl -X POST http://localhost:8000/api/v1/batch/reset \
  -H "Content-Type: application/json" \
  -d '{"force": true}'
```

### Q: Scraper finds 0 results for a test
**A:** 
1. Website may be blocking automated requests
2. Test name doesn't match lab's naming
3. Lab temporarily down
→ Logs show detailed error info

### Q: Database shows fewer records than expected
**A:**
1. Some labs failed (gracefully skipped)
2. Check success_rate in batch results
3. View logs for which labs failed

### Q: How to run only specific labs?
**A:** Not supported yet. Modify `batch_test_scraper.py`:
- Comment out unwanted lab scrapers in `scrape_test_all_labs()`
- Adjust `total_requested` calculation

---

## Performance Notes

### Timing Estimates

- **Per test (4 labs concurrent):** ~3-4 seconds
- **Per batch (10 tests):** ~2-3 minutes
- **All tests (103 total):** ~23 minutes
- **Custom batch size 20:** ~5-6 minutes per batch = ~18 minutes total

### Database Impact

- **Insert per batch:** 30-40 new records (successful scrapes)
- **Update per batch:** Mark old prices as `is_latest = 0`
- **Query load:** Minimal (only during status checks)
- **Disk space:** ~1MB per 1000 price records

---

## API Responses Reference

### Success Response (202)
```json
{
  "success": true,
  "message": "Batch scraping started in background",
  "total_batches": 11,
  "total_tests": 103
}
```

### Error Response (400/500)
```json
{
  "detail": "Error message describing what went wrong"
}
```

### Status Response (200)
```json
{
  "status": "running|completed|idle|error",
  "progress_percent": 25.5,
  "completed_batches": 3,
  "total_batches": 11,
  "batches": {
    "1": { "status": "completed", "results": {...} },
    "2": { "status": "completed", "results": {...} }
  }
}
```

---

## Support

For issues or questions:
1. Check logs: `logs/batch_scraper.log`
2. Review status: `GET /api/v1/batch/status`
3. Verify database: Check `test_prices` table
4. Reset if needed: `POST /api/v1/batch/reset`

---

**Version:** 1.0.0  
**Last Updated:** 2026-02-20  
**Status:** Production Ready ✅

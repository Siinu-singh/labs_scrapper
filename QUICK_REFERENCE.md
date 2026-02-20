# 🚀 BATCH SCRAPER API - QUICK REFERENCE

## 📋 File Structure

```
scrapper_api/
├── src/
│   ├── api/
│   │   ├── batch_routes.py          ✨ NEW - Batch scraper endpoints
│   │   └── routes.py                ✏️ UPDATED - Includes batch routes
│   │
│   ├── controllers/
│   │   └── batch_scraper_controller.py  ✨ NEW - API request handler
│   │
│   ├── services/
│   │   └── batch_scraper_service.py     ✨ NEW - Batch execution logic
│   │
│   ├── schemas/
│   │   └── scraper_schemas.py       ✏️ UPDATED - Batch request/response models
│   │
│   └── utils/
│       └── batch_state_manager.py   ✨ NEW - State tracking & persistence
│
├── batch_test_scraper.py            ✏️ UPDATED - Added batch support
│
├── Batch_Scraper_API.postman_collection.json  ✨ NEW - Ready for Postman import
│
└── BATCH_SCRAPER_API_README.md     ✨ NEW - Full documentation
```

---

## 🎯 3-Step Quick Start

### Step 1: Start Server
```bash
cd /home/suraj-kumar/Desktop/scrapper/scrapper_api
source venv/bin/activate
python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Step 2: Import Postman Collection
- Open Postman
- Import → `Batch_Scraper_API.postman_collection.json`
- Base URL: `http://localhost:8000`

### Step 3: Start Scraping
```
POST /api/v1/batch/start
{
  "total_batches": null,
  "batch_size": 10
}
```

---

## 📊 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check |
| **POST** | **`/api/v1/batch/start`** | Start batch scraping |
| **GET** | **`/api/v1/batch/status`** | Get progress & results |
| POST | `/api/v1/batch/reset` | Reset state |

---

## 💡 Usage Examples

### Scrape All 103 Tests
```json
POST /api/v1/batch/start
{
  "total_batches": null,
  "batch_size": 10
}
```
**Time:** ~23 minutes | **Batches:** 11

### Quick Test (1 Batch)
```json
POST /api/v1/batch/start
{
  "total_batches": 1,
  "batch_size": 10
}
```
**Time:** ~2-3 minutes

### Monitor Progress
```
GET /api/v1/batch/status
```
Returns:
- Current batch number
- Progress percentage
- Completed batches
- Individual batch results

---

## 🏗️ Architecture

```
Request (Postman)
    ↓
FastAPI Server (Port 8000)
    ↓
    ├→ Return 202 Accepted immediately
    │
    └→ Background Task:
       ├ Load batch of tests
       ├ Scrape from 4 labs (concurrent)
       ├ Parse prices
       ├ Save to database (is_latest = 1)
       ├ Update batch_state.json
       └ Repeat for next batch

User can monitor with GET /api/v1/batch/status
```

---

## 🔧 Key Features

✅ **Background Processing** - Non-blocking API responses  
✅ **Progress Tracking** - Real-time monitoring via status endpoint  
✅ **State Persistence** - `batch_state.json` survives restarts  
✅ **Graceful Failure** - Skip failed labs, continue processing  
✅ **Batch Resuming** - Auto-skip completed batches  
✅ **Production Ready** - Logging, error handling, validation  
✅ **Cron Compatible** - Easy automation in production  

---

## 📈 Performance

| Metric | Value |
|--------|-------|
| Tests per batch | 10 (configurable: 1-50) |
| Labs per test | 4 (concurrent) |
| Time per batch | 2-3 minutes |
| Total tests | 103 |
| Total batches | 11 |
| Total time | ~23 minutes |
| Success rate | 80-100% per lab |

---

## 📝 Logging

Logs stored in: `logs/batch_scraper.log`

Example log entry:
```
2026-02-20 15:30:00 - INFO - Starting batch scraping: 103 tests, 11 batches of size 10
2026-02-20 15:30:05 - INFO - Starting batch 1/11
2026-02-20 15:32:00 - INFO - Batch 1 completed: 34 records saved
2026-02-20 15:32:05 - INFO - Starting batch 2/11
...
```

---

## 🗄️ Database

New/Updated records in `test_prices` table:

```sql
-- Check latest prices
SELECT COUNT(*) FROM test_prices WHERE is_latest = 1;

-- Verify all 4 labs
SELECT lab_name, COUNT(*) as count 
FROM test_prices 
WHERE is_latest = 1 
GROUP BY lab_name;
```

---

## ⚙️ Configuration

**In `StartBatchScrapingRequest`:**
```python
total_batches: Optional[int] = None  # null = all tests
batch_size: int = 10                # tests per batch (1-50)
```

**For production cron:**
```bash
0 2 * * * curl -X POST http://localhost:8000/api/v1/batch/start \
  -H "Content-Type: application/json" \
  -d '{"total_batches": null, "batch_size": 10}'
```

---

## 🐛 Troubleshooting

### Endpoint Not Found
- Verify server is running
- Check logs in `/tmp/server.log`
- Try: `curl http://localhost:8000/health`

### Batch Stuck on Running
```bash
curl -X POST http://localhost:8000/api/v1/batch/reset \
  -H "Content-Type: application/json" \
  -d '{"force": true}'
```

### Database Shows 0 Records
- Check success_rate in batch results
- View logs for lab failures
- Some labs may be temporarily down

---

## 📚 Files to Review

1. **`Batch_Scraper_API.postman_collection.json`** - Import in Postman
2. **`BATCH_SCRAPER_API_README.md`** - Full documentation  
3. **`src/api/batch_routes.py`** - Endpoint definitions
4. **`src/services/batch_scraper_service.py`** - Core logic
5. **`src/utils/batch_state_manager.py`** - State management
6. **`batch_test_scraper.py`** - Scraper with batch support

---

## ✨ What's New

### API Endpoints
- `POST /api/v1/batch/start` - Start batch scraping
- `GET /api/v1/batch/status` - Monitor progress
- `POST /api/v1/batch/reset` - Reset state

### Classes & Services
- `BatchStateManager` - Persistent state tracking
- `BatchScraperService` - Orchestrates batch execution
- `BatchScraperController` - Handles API requests
- `batch_routes` - FastAPI endpoints

### Database Features
- `batch_state.json` - Tracks completed batches
- Resume from last batch if interrupted
- Individual batch result logging

---

## 🎓 Learning Path

1. Start server: `python3 -m uvicorn src.main:app ...`
2. Import Postman collection
3. Call `/api/v1/batch/start` with 1 batch
4. Monitor `/api/v1/batch/status`
5. See results logged and saved to DB
6. Understand the workflow
7. Run full batch (all 103 tests)

---

## 📞 Support

**Logs:** `logs/batch_scraper.log`  
**State:** `batch_state.json`  
**Status:** `GET /api/v1/batch/status`  
**Docs:** `BATCH_SCRAPER_API_README.md`  

---

**Status:** ✅ Production Ready  
**Version:** 1.0.0  
**Last Updated:** 2026-02-20  

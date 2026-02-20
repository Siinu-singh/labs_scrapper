"""
BATCH SCRAPER API - POSTMAN QUICK START GUIDE
===============================================

This document provides Postman request examples for the Batch Scraper API.
Copy-paste the following requests into Postman to test the API.

BASE URL: http://localhost:8000 (development)
         https://api.yourdomain.com (production)

=================================================================================
1. START BATCH SCRAPING - POST /api/v1/batch/start
=================================================================================

URL: POST http://localhost:8000/api/v1/batch/start

Headers:
  Content-Type: application/json

Body (JSON):
{
  "total_batches": null,
  "batch_size": 10
}

EXPLANATION:
- total_batches: null → Automatically scrapes all 103 tests (11 batches of 10 each)
- total_batches: 3 → Scrapes only first 3 batches (30 tests)
- batch_size: 10 → Each batch processes 10 tests × 4 labs = 40 operations

Expected Response (202 Accepted):
{
  "success": true,
  "message": "Batch scraping started in background",
  "batch_size": 10,
  "total_batches": 11,
  "total_tests": 103
}

NOTES:
- Returns 202 Accepted immediately (scraping runs in background)
- API continues to accept requests while scraping
- Use /api/v1/batch/status to monitor progress
- Estimated time: ~23 minutes for all 103 tests


=================================================================================
2. GET BATCH STATUS - GET /api/v1/batch/status
=================================================================================

URL: GET http://localhost:8000/api/v1/batch/status

Headers: (none required)

Expected Response (200 OK):
{
  "status": "running",
  "message": null,
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
        "total_operations": 40,
        "successful": 34,
        "failed": 6,
        "success_rate": 85.0,
        "saved_count": 34,
        "duration_seconds": 129.5
      }
    },
    "2": {
      "status": "completed",
      "completed_at": "2026-02-20T15:34:00.123456",
      "results": {
        "batch": 2,
        "success": true,
        ...
      }
    },
    "3": {
      "status": "pending",
      "completed_at": null,
      "results": null
    }
  }
}

RESPONSE STATUS MEANINGS:
- status: "idle" → No scraping in progress
- status: "running" → Batch scraping is active
- status: "completed" → All batches finished
- status: "error" → Something went wrong

PROGRESS TRACKING:
- progress_percent: 18.18 → 18.18% complete (2 of 11 batches done)
- completed_batches: 2 → 2 batches finished
- current_batch: 3 → Currently processing batch 3
- Check batches.{batch_num}.status for individual batch status


=================================================================================
3. RESET BATCH STATE - POST /api/v1/batch/reset
=================================================================================

URL: POST http://localhost:8000/api/v1/batch/reset

Headers:
  Content-Type: application/json

Body (JSON):
{
  "force": false
}

Expected Response (200 OK):
{
  "success": true,
  "message": "Batch state reset successfully"
}

USE CASES:
- force: false (default) → Prevents reset if scraping is running
- force: true → Force reset even if scraping is in progress

ERROR Response (400 Bad Request):
{
  "success": false,
  "error": "Batch scraping in progress. Use force=true to override"
}


=================================================================================
TYPICAL WORKFLOW
=================================================================================

1. RESET STATE (optional, for clean start):
   POST /api/v1/batch/reset
   Body: {"force": false}

2. START BATCH SCRAPING:
   POST /api/v1/batch/start
   Body: {"total_batches": null, "batch_size": 10}
   ➜ Returns 202 Accepted immediately

3. MONITOR PROGRESS (poll every 30-60 seconds):
   GET /api/v1/batch/status
   ➜ Returns current progress, batch statuses, and detailed results

4. WAIT FOR COMPLETION:
   Keep polling /api/v1/batch/status until:
   - status = "completed"
   - OR progress_percent = 100
   - OR completed_batches = total_batches


=================================================================================
EXAMPLE: SCRAPE ONLY 2 BATCHES (20 TESTS)
=================================================================================

POST /api/v1/batch/start

{
  "total_batches": 2,
  "batch_size": 10
}

This will:
- Process batch 1 (tests 1-10)
- Process batch 2 (tests 11-20)
- Skip batches 3-11
- Take approximately 5 minutes


=================================================================================
EXAMPLE: CUSTOM BATCH SIZE (15 TESTS PER BATCH)
=================================================================================

POST /api/v1/batch/start

{
  "total_batches": null,
  "batch_size": 15
}

This will:
- 103 tests ÷ 15 = 7 batches
- 7 batches × ~2.5 minutes = ~17.5 minutes total
- Fewer, longer batches


=================================================================================
ERROR HANDLING
=================================================================================

If scraping fails mid-batch:
- That lab is SKIPPED for that test
- Other labs continue processing
- Batch completes with partial results
- View batch results in /api/v1/batch/status response

Example partial result:
{
  "test_id": 5,
  "test_name": "Hemoglobin",
  "results": [
    {"lab": "redcliffe", "status": "success", "price": 99},
    {"lab": "orange", "status": "failed", "error": "Connection timeout"},
    {"lab": "1mg", "status": "success", "price": 99},
    {"lab": "lalpathlabs", "status": "success", "price": 120}
  ]
}


=================================================================================
MONITORING IN PRODUCTION
=================================================================================

1. Check logs directory: logs/
   - batch_scraper.log → Contains all batch scraping operations
   - app.log → Contains API operations

2. Check batch_state.json: 
   - Stores persistent state of batch operations
   - Allows resuming from last batch if interrupted

3. Database:
   - View test_prices table for scraped results
   - is_latest = 1 → Most recent scrape
   - Check scraped_at timestamp for when prices were updated


=================================================================================
TROUBLESHOOTING
=================================================================================

Q: Endpoint returns 500 error
A: Check server logs (logs/app.log) for detailed error messages

Q: Batch gets stuck (status shows running but no progress)
A: Restart server or call /api/v1/batch/reset with force=true

Q: Some labs keep failing
A: Website may be blocking automated requests. Check individual lab websites
   for rate limiting or bot detection

Q: Database shows 0 saved records
A: Scraper may have failed. Check logs and verify database connection

Q: How to resume if interrupted?
A: Simply call POST /api/v1/batch/start again with same parameters
   API will skip already completed batches and continue from next batch


=================================================================================
"""

print(__doc__)

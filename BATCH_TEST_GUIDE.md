# Batch Test Scraper - 10 Tests × 4 Labs Guide

## Overview

This guide walks you through testing the scraper system with 10 tests from your database, scraping from all 4 labs concurrently, and saving results to the database.

**Configuration:**
- Tests: First 10 from database (IDs 1-10)
- Labs: Orange Health, Redcliffe Labs, Lal Path Labs, 1mg
- Total Operations: 40 scrape requests
- Execution: Concurrent (all 4 labs in parallel per test)
- Duration: ~2-3 minutes
- Output: Save to `test_prices` table + Console display

---

## Step 1: Create the Batch Test Script

Create file: `batch_test_scraper.py`

```python
#!/usr/bin/env python3
"""
Batch Test Scraper - Test 10 tests from all 4 labs
Scrapes 10 tests concurrently from all 4 labs (40 total operations)
Saves results to test_prices table and displays summary
"""
import sys
sys.path.insert(0, '/home/suraj-kumar/Desktop/scrapper/scrapper_api')

import asyncio
import time
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import settings
from src.models.test_models import Test, TestPrice
from src.scrapers.onemg_scraper import scrape_1mg
from src.scrapers.orange_scraper import scrape_orange
from src.scrapers.redcliffe_scraper import scrape_redcliffe
from src.scrapers.lalpathlabs_scraper import scrape_lalpathlabs
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class BatchTestScraper:
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.start_time = None
        self.results = []
        self.stats = {
            "total_requested": 0,
            "total_successful": 0,
            "total_failed": 0,
            "by_lab": {
                "orange": {"success": 0, "failed": 0},
                "redcliffe": {"success": 0, "failed": 0},
                "lalpathlabs": {"success": 0, "failed": 0},
                "1mg": {"success": 0, "failed": 0},
            }
        }

    def print_header(self, title):
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}\n")

    def get_first_10_tests(self):
        """Get first 10 tests from database"""
        db = self.SessionLocal()
        try:
            tests = db.query(Test).filter(Test.is_active == True).limit(10).all()
            return [(t.id, t.test_name) for t in tests]
        finally:
            db.close()

    async def scrape_test_all_labs(self, test_id: int, test_name: str):
        """Scrape one test from all 4 labs concurrently"""
        logger.info(f"Starting scrape for test: {test_name}")
        
        results = await asyncio.gather(
            self.scrape_and_record(test_id, test_name, "orange", scrape_orange),
            self.scrape_and_record(test_id, test_name, "redcliffe", scrape_redcliffe),
            self.scrape_and_record(test_id, test_name, "lalpathlabs", scrape_lalpathlabs),
            self.scrape_and_record(test_id, test_name, "1mg", scrape_1mg),
            return_exceptions=True
        )
        
        return {
            "test_id": test_id,
            "test_name": test_name,
            "results": results
        }

    async def scrape_and_record(self, test_id: int, test_name: str, lab_name: str, scraper_func):
        """Scrape from one lab and record result"""
        try:
            scrape_results = await scraper_func(test_name)
            
            if scrape_results and len(scrape_results) > 0:
                best_match = scrape_results[0]
                
                self.results.append({
                    "test_id": test_id,
                    "test_name": test_name,
                    "lab_name": lab_name,
                    "price": best_match.get("price"),
                    "matched_test_name": best_match.get("test_name"),
                    "match_score": best_match.get("match_score", 0.0),
                    "status": "success"
                })
                
                self.stats["total_successful"] += 1
                self.stats["by_lab"][lab_name]["success"] += 1
                
                return {
                    "lab": lab_name,
                    "status": "success",
                    "price": best_match.get("price"),
                    "matched_as": best_match.get("test_name")
                }
            else:
                self.results.append({
                    "test_id": test_id,
                    "test_name": test_name,
                    "lab_name": lab_name,
                    "status": "no_match"
                })
                
                self.stats["total_failed"] += 1
                self.stats["by_lab"][lab_name]["failed"] += 1
                
                return {
                    "lab": lab_name,
                    "status": "no_match",
                    "error": "No results found"
                }
                
        except Exception as e:
            self.results.append({
                "test_id": test_id,
                "test_name": test_name,
                "lab_name": lab_name,
                "status": "failed",
                "error": str(e)
            })
            
            self.stats["total_failed"] += 1
            self.stats["by_lab"][lab_name]["failed"] += 1
            
            logger.error(f"Error scraping {test_name} from {lab_name}: {str(e)}")
            return {
                "lab": lab_name,
                "status": "failed",
                "error": str(e)
            }

    def save_to_database(self):
        """Save all results to test_prices table"""
        db = self.SessionLocal()
        try:
            saved_count = 0
            
            for result in self.results:
                if result["status"] == "success":
                    # Mark old records as not latest
                    db.query(TestPrice).filter(
                        (TestPrice.test_id == result["test_id"]) &
                        (TestPrice.lab_name == result["lab_name"]) &
                        (TestPrice.is_latest == True)
                    ).update({"is_latest": False})
                    
                    # Insert new record
                    price_record = TestPrice(
                        test_id=result["test_id"],
                        lab_name=result["lab_name"],
                        price=result.get("price"),
                        matched_test_name=result.get("matched_test_name"),
                        match_score=result.get("match_score"),
                        is_available=True,
                        scraped_at=datetime.now(),
                        is_latest=True
                    )
                    db.add(price_record)
                    saved_count += 1
            
            db.commit()
            logger.info(f"Saved {saved_count} records to database")
            return saved_count
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving to database: {str(e)}")
            return 0
        finally:
            db.close()

    def display_results(self):
        """Display results in console"""
        self.print_header("📊 BATCH TEST RESULTS")
        
        # Overall summary
        duration = time.time() - self.start_time
        success_rate = (self.stats["total_successful"] / self.stats["total_requested"] * 100) if self.stats["total_requested"] > 0 else 0
        
        print(f"⏱️  Duration: {duration:.1f} seconds")
        print(f"📊 Total Operations: {self.stats['total_requested']}")
        print(f"✅ Successful: {self.stats['total_successful']}")
        print(f"❌ Failed: {self.stats['total_failed']}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # By lab summary
        print(f"\n📋 Results by Lab:")
        for lab_name, stats in self.stats["by_lab"].items():
            total = stats["success"] + stats["failed"]
            pct = stats["success"]/total*100 if total > 0 else 0
            print(f"  {lab_name.upper():15} - Success: {stats['success']:2}/{total:2} ({pct:.0f}%)")
        
        # By test summary
        self.print_header("🧪 Results by Test")
        
        tests_seen = {}
        for result in self.results:
            test_name = result["test_name"]
            if test_name not in tests_seen:
                tests_seen[test_name] = []
            tests_seen[test_name].append(result)
        
        for test_name, test_results in tests_seen.items():
            print(f"📌 {test_name}")
            for result in test_results:
                status_symbol = "✅" if result["status"] == "success" else "❌"
                price_str = f"${result.get('price')}" if result.get("price") else "N/A"
                matched = result.get("matched_test_name", "N/A")
                print(f"   {status_symbol} {result['lab_name']:12} - Price: {price_str:8} (matched as: {matched})")
        
        # Database summary
        self.print_header("💾 Database Summary")
        
        db = self.SessionLocal()
        try:
            total_tests = db.query(Test).count()
            total_prices = db.query(TestPrice).count()
            latest_prices = db.query(TestPrice).filter(TestPrice.is_latest == True).count()
            
            print(f"Tests in Database: {total_tests}")
            print(f"Total Price Records: {total_prices}")
            print(f"Latest Prices: {latest_prices}")
            
        finally:
            db.close()

    async def run(self):
        """Main execution method"""
        self.print_header("🚀 BATCH TEST SCRAPER - 10 TESTS × 4 LABS")
        
        # Get tests
        tests = self.get_first_10_tests()
        self.stats["total_requested"] = len(tests) * 4  # 10 tests × 4 labs
        
        print(f"📝 Tests to Scrape: {len(tests)}")
        print(f"🏥 Labs to Scrape: 4 (Orange, Redcliffe, Lal Path Labs, 1mg)")
        print(f"📊 Total Operations: {self.stats['total_requested']}")
        print(f"⏱️  Estimated Duration: 2-3 minutes\n")
        
        # Show test list
        print("Tests to be scraped:")
        for idx, (test_id, test_name) in enumerate(tests, 1):
            print(f"  {idx:2}. {test_name}")
        
        # Start timer
        self.start_time = time.time()
        self.print_header("⏳ SCRAPING IN PROGRESS...")
        
        # Scrape all tests concurrently
        tasks = [self.scrape_test_all_labs(test_id, test_name) for test_id, test_name in tests]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Save results to database
        print("💾 Saving results to database...")
        saved_count = self.save_to_database()
        print(f"✅ Saved {saved_count} records to test_prices table\n")
        
        # Display results
        self.display_results()
        
        self.print_header("✅ BATCH TEST COMPLETE")
        print(f"""
Next Steps:
1. Review the results above
2. Check database: SELECT * FROM test_prices LIMIT 20;
3. If successful, proceed to batch scraping all 103 tests
4. Setup automated cron job with APScheduler for periodic updates

Your database is now ready for production scraping!
        """)

def main():
    print("\n" + "="*70)
    print("  BATCH TEST SCRAPER - 10 Tests × 4 Labs")
    print("="*70)
    
    scraper = BatchTestScraper()
    asyncio.run(scraper.run())

if __name__ == "__main__":
    main()
```

---

## Step 2: Run the Script

```bash
cd /home/suraj-kumar/Desktop/scrapper/scrapper_api
source venv/bin/activate
python batch_test_scraper.py
```

Expected output:
```
======================================================================
  BATCH TEST SCRAPER - 10 Tests × 4 Labs
======================================================================

📝 Tests to Scrape: 10
🏥 Labs to Scrape: 4 (Orange, Redcliffe, Lal Path Labs, 1mg)
📊 Total Operations: 40
⏱️  Estimated Duration: 2-3 minutes

Tests to be scraped:
   1. Bilirubin Profile
   2. Iron Profile
   3. Lipid Profile
   4. Thyroid Function Test (TFT)
   5. Complete Blood Count (CBC)
   6. Hemoglobin (Hb)
   7. Blood Group ABO & Rh Typing
   8. Blood Glucose Fasting
   9. Blood Glucose Post Prandial
  10. HbA1c

======================================================================
  ⏳ SCRAPING IN PROGRESS...
======================================================================

[Scraping happens here - takes 2-3 minutes]

======================================================================
  📊 BATCH TEST RESULTS
======================================================================

⏱️  Duration: 157.3 seconds
📊 Total Operations: 40
✅ Successful: 35
❌ Failed: 5
📈 Success Rate: 87.5%

📋 Results by Lab:
  ORANGE          - Success: 10/10 (100%)
  REDCLIFFE       - Success:  8/10 (80%)
  LALPATHLABS     - Success:  9/10 (90%)
  1MG             - Success:  8/10 (80%)

[Results by test shown here]

======================================================================
  💾 Database Summary
======================================================================

Tests in Database: 103
Total Price Records: 35
Latest Prices: 35

======================================================================
  ✅ BATCH TEST COMPLETE
======================================================================
```

---

## Step 3: Verify Results in Database

```bash
mysql -u root -p scraper_db

# Check total price records
SELECT COUNT(*) FROM test_prices;

# View sample prices
SELECT t.test_name, tp.lab_name, tp.price, tp.matched_test_name
FROM test_prices tp
JOIN tests t ON t.id = tp.test_id
LIMIT 20;

# Check prices for specific test
SELECT tp.lab_name, tp.price, tp.matched_test_name
FROM test_prices tp
WHERE tp.test_id = 1
ORDER BY tp.lab_name;
```

---

## Step 4: What to Expect

### Success Scenario (80-100% success rate)
- All or most labs find matches for tests
- Prices are stored in database
- You can proceed to full batch scraping

### Partial Success (50-80%)
- Some labs work better than others
- May indicate website layout changes on some platforms
- Still valid - continue with caution
- Consider fixing matching algorithm for failing labs

### Low Success (<50%)
- Indicates issues with scraper logic
- May need debugging individual lab scrapers
- Check logs for specific errors
- Verify website URLs are still correct

---

## Next Steps After Test

### If Successful ✅
1. Run full batch on all 103 tests
2. Setup APScheduler for automated 6-hour updates
3. Create API endpoints for users to fetch prices
4. Deploy to production

### If Issues Found ⚠️
1. Check logs for error messages
2. Debug specific lab scrapers
3. Verify matching algorithm is working
4. Test individual lab scrapers separately

---

## Troubleshooting

### Common Issues

**No results found:**
- Indicates matching algorithm not finding close matches
- Check the matching score output
- May need to improve semantic matching

**Website timeouts:**
- Indicates scraper is too slow
- Check if websites are blocking automated requests
- May need to add user-agent headers
- Consider adding delays between requests

**Connection refused:**
- Database connection issue
- Verify MySQL is running
- Check credentials in config.py

**Memory errors:**
- 40 concurrent requests might be too many
- Reduce from 4 labs to 2 labs for testing
- Or reduce concurrent connections

---

## Success Criteria

✅ Script runs without crashes
✅ At least 30/40 operations successful (75%+)
✅ Prices stored in test_prices table
✅ Console output shows results clearly

When all criteria met → Ready for production batch scraping!


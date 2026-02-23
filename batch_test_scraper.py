import asyncio
import re
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
    
    def get_all_active_tests(self):
        """Get all active tests from database"""
        db = self.SessionLocal()
        try:
            tests = db.query(Test).filter(Test.is_active == True).all()
            return [(t.id, t.test_name) for t in tests]
        finally:
            db.close()
    
    def get_tests_by_batch(self, batch_num: int, batch_size: int = 10):
        """Get tests for a specific batch"""
        db = self.SessionLocal()
        try:
            offset = (batch_num - 1) * batch_size
            tests = db.query(Test).filter(Test.is_active == True).offset(offset).limit(batch_size).all()
            return [(t.id, t.test_name) for t in tests]
        finally:
            db.close()

    async def scrape_test_all_labs(self, test_id: int, test_name: str):
        """Scrape one test from 2 labs concurrently"""
        logger.info(f"Starting scrape for test: {test_name}")
        
        # Pair 1 (Orange + Redcliffe - run together):
            # Pair 1 (Orange + Redcliffe - run together):
        results_pair1 = await asyncio.gather(
            self.scrape_and_record(test_id, test_name, "orange", scrape_orange),
            self.scrape_and_record(test_id, test_name, "redcliffe", scrape_redcliffe),
            return_exceptions=True
        )
        # Then Pair 2 (1mg + Lal Path Labs - run together after Pair 1 finishes):
        results_pair2 = await asyncio.gather(
            self.scrape_and_record(test_id, test_name, "1mg", scrape_1mg),
            self.scrape_and_record(test_id, test_name, "lalpathlabs", scrape_lalpathlabs),
            return_exceptions=True
    )
        # Combine results:
        results = results_pair1 + results_pair2
        
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
                    # Parse price to extract numeric value
                    price_value = self._parse_price(result.get("price"))
                    
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
                        price=price_value,
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
    
    def _parse_price(self, price_str):
        """Extract numeric value from price string (handles currency symbols)"""
        if not price_str:
            return None
        
        # Convert to string if not already
        price_str = str(price_str).strip()
        
        # Remove currency symbols and non-numeric characters (except decimal point)
        numeric_str = re.sub(r'[^\d.]', '', price_str)
        
        # Convert to float, return None if empty
        if numeric_str:
            try:
                return float(numeric_str)
            except ValueError:
                return None
        return None

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

    async def run(self, batch_num: int = 1, batch_size: int = 10, total_batches: int = 1):
        """Main execution method with batch support"""
        self.print_header(f"🚀 BATCH SCRAPER - Batch {batch_num}/{total_batches}")
        
        # Get tests for this batch
        tests = self.get_tests_by_batch(batch_num, batch_size)
        
        if not tests:
            print(f"❌ No tests found for batch {batch_num}")
            return {"batch": batch_num, "success": False, "error": "No tests found"}
        
        self.stats["total_requested"] = len(tests) * 4  # N tests × 4 labs
        
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
        tasks = [self.scrape_test_all_labs(int(test_id), str(test_name)) for test_id, test_name in tests]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Save results to database
        print("💾 Saving results to database...")
        saved_count = self.save_to_database()
        print(f"✅ Saved {saved_count} records to test_prices table\n")
        
        # Display results
        self.display_results()
        
        return {
            "batch": batch_num,
            "success": True,
            "total_tests": len(tests),
            "total_operations": self.stats["total_requested"],
            "successful": self.stats["total_successful"],
            "failed": self.stats["total_failed"],
            "success_rate": (self.stats["total_successful"] / self.stats["total_requested"] * 100) if self.stats["total_requested"] > 0 else 0,
            "saved_count": saved_count,
            "duration_seconds": time.time() - self.start_time
        }


if __name__ == "__main__":
    scraper = BatchTestScraper()
    asyncio.run(scraper.run())
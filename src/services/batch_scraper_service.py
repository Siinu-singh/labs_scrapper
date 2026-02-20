"""
Batch scraper service for managing batch-wise test scraping
"""

import asyncio
from typing import Dict, Any, Optional
from batch_test_scraper import BatchTestScraper
from src.utils.batch_state_manager import BatchStateManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class BatchScraperService:
    """Service for managing batch scraping operations"""
    
    def __init__(self):
        self.state_manager = BatchStateManager()
        self.scraper = None
    
    async def start_batch_scraping(self, total_batches: Optional[int] = None, batch_size: int = 10) -> Dict[str, Any]:
        """
        Start batch scraping for all tests or specified number of batches
        
        Args:
            total_batches: Number of batches to scrape. If None, calculates from total active tests
            batch_size: Number of tests per batch (default: 10)
        
        Returns:
            Status dict with batch scraping details
        """
        try:
            # Initialize scraper to get total tests
            self.scraper = BatchTestScraper()
            
            # Get total active tests
            all_tests = self.scraper.get_all_active_tests()
            total_tests = len(all_tests)
            
            # Calculate total batches if not provided
            if total_batches is None:
                total_batches = (total_tests + batch_size - 1) // batch_size
            
            logger.info(f"Starting batch scraping: {total_tests} tests, {total_batches} batches of size {batch_size}")
            
            # Initialize state
            self.state_manager.start_batch_scraping(total_batches, batch_size)
            
            # Scrape each batch
            for batch_num in range(1, total_batches + 1):
                try:
                    logger.info(f"Starting batch {batch_num}/{total_batches}")
                    
                    # Create fresh scraper for each batch to avoid state pollution
                    scraper = BatchTestScraper()
                    
                    # Run batch
                    result = await scraper.run(batch_num, batch_size, total_batches)
                    
                    # Update state
                    self.state_manager.update_batch_status(batch_num, "completed", result)
                    
                    logger.info(f"Batch {batch_num} completed: {result['saved_count']} records saved")
                    
                except Exception as e:
                    logger.error(f"Error in batch {batch_num}: {str(e)}", exc_info=True)
                    self.state_manager.update_batch_status(batch_num, "failed", {"error": str(e)})
            
            # Mark overall scraping as complete
            self.state_manager.mark_complete()
            
            return {
                "success": True,
                "message": "Batch scraping completed",
                "total_batches": total_batches,
                "total_tests": total_tests
            }
            
        except Exception as e:
            logger.error(f"Error starting batch scraping: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_scraping_status(self) -> Dict[str, Any]:
        """Get current status of batch scraping"""
        return self.state_manager.get_status()
    
    def reset_batch_state(self):
        """Reset batch state for new run"""
        self.state_manager.reset_state()
        logger.info("Batch state reset")
        return {"message": "Batch state reset successfully"}

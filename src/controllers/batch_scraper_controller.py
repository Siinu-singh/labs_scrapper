"""
Batch scraper controller for handling batch scraping API requests
"""

from typing import Dict, Any
from src.services.batch_scraper_service import BatchScraperService
from src.utils.logger import setup_logger
from fastapi import BackgroundTasks

logger = setup_logger(__name__)

class BatchScraperController:
    """Controller for batch scraper operations"""
    
    def __init__(self):
        self.service = BatchScraperService()
    
    async def start_batch_scraping(self, total_batches=None, batch_size=10, background_tasks: BackgroundTasks = None) -> Dict[str, Any]:
        """
        Start batch scraping in background
        """
        try:
            logger.info(f"Batch scraping requested: total_batches={total_batches}, batch_size={batch_size}")
            
            # Add to background tasks if available (for async execution)
            if background_tasks:
                background_tasks.add_task(
                    self.service.start_batch_scraping,
                    total_batches,
                    batch_size
                )
                return {
                    "success": True,
                    "message": "Batch scraping started in background",
                    "batch_size": batch_size
                }
            else:
                # For direct execution (not in background)
                result = await self.service.start_batch_scraping(total_batches, batch_size)
                return result
            
        except Exception as e:
            logger.error(f"Error starting batch scraping: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_batch_status(self) -> Dict[str, Any]:
        """Get current batch scraping status"""
        try:
            status = self.service.get_scraping_status()
            return status
        except Exception as e:
            logger.error(f"Error getting batch status: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }
    
    def reset_batch_state(self, force=False) -> Dict[str, Any]:
        """Reset batch state"""
        try:
            status = self.service.get_scraping_status()
            
            # Prevent reset if scraping is in progress unless force=True
            if status.get("status") == "running" and not force:
                return {
                    "success": False,
                    "error": "Batch scraping in progress. Use force=true to override"
                }
            
            self.service.reset_batch_state()
            logger.info("Batch state reset")
            
            return {
                "success": True,
                "message": "Batch state reset successfully"
            }
        except Exception as e:
            logger.error(f"Error resetting batch state: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }


# Global instance
batch_scraper_controller = BatchScraperController()

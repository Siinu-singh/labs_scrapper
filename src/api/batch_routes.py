from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from src.schemas.scraper_schemas import (
    StartBatchScrapingRequest,
    BatchScrapingResponse,
    BatchStatusResponse,
    ResetBatchStateRequest
)
from src.controllers.batch_scraper_controller import batch_scraper_controller
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1/batch", tags=["Batch Scraper"])

@router.post(
    "/start",
    response_model=BatchScrapingResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start batch scraping",
    description="Start scraping all tests in batches (runs in background)"
)
async def start_batch_scraping(
    request: StartBatchScrapingRequest,
    background_tasks: BackgroundTasks
) -> BatchScrapingResponse:
    """
    Start batch scraping for all active tests
    
    - **total_batches**: Total number of batches (optional, auto-calculated if null)
    - **batch_size**: Number of tests per batch (1-50, default: 10)
    
    Returns: 202 Accepted - scraping started in background
    """
    try:
        result = await batch_scraper_controller.start_batch_scraping(
            total_batches=request.total_batches,
            batch_size=request.batch_size,
            background_tasks=background_tasks
        )
        
        if result.get("success"):
            return BatchScrapingResponse(
                success=True,
                message=result.get("message"),
                total_batches=result.get("total_batches"),
                total_tests=result.get("total_tests")
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Unknown error")
            )
    except Exception as e:
        logger.error(f"Error starting batch scraping: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/status",
    response_model=BatchStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get batch scraping status",
    description="Get current status of batch scraping progress"
)
async def get_batch_status() -> BatchStatusResponse:
    """
    Get current batch scraping status
    
    Returns:
    - status: idle, running, completed, or error
    - progress_percent: Percentage of batches completed
    - completed_batches: Number of completed batches
    - total_batches: Total batches to scrape
    """
    try:
        status_data = batch_scraper_controller.get_batch_status()
        
        return BatchStatusResponse(
            status=status_data.get("status"),
            message=status_data.get("message"),
            current_batch=status_data.get("current_batch"),
            total_batches=status_data.get("total_batches"),
            completed_batches=status_data.get("completed_batches"),
            progress_percent=status_data.get("progress_percent"),
            batch_size=status_data.get("batch_size"),
            started_at=status_data.get("started_at"),
            batches=status_data.get("batches")
        )
    except Exception as e:
        logger.error(f"Error getting batch status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post(
    "/reset",
    status_code=status.HTTP_200_OK,
    summary="Reset batch state",
    description="Reset batch scraping state (useful for retrying)"
)
async def reset_batch_state(request: ResetBatchStateRequest):
    """
    Reset batch scraping state
    
    - **force**: Force reset even if scraping is in progress (default: false)
    """
    try:
        result = batch_scraper_controller.reset_batch_state(force=request.force)
        
        if result.get("success"):
            return {
                "success": True,
                "message": result.get("message")
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error")
            )
    except Exception as e:
        logger.error(f"Error resetting batch state: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

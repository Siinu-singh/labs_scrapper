from fastapi import HTTPException
from src.schemas.scraper_schemas import ScrapeRequest, ScrapeResponse, ComparisonRequest, ComparisonResponse
from src.services.scraper_service import scraper_service
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ScraperController:
    async def scrape_test(self, request: ScrapeRequest) -> ScrapeResponse:
        results = await scraper_service.scrape_test(request.test_name, request.lab_name)
        return ScrapeResponse(
            lab=request.lab_name.value,
            test_searched=request.test_name,
            results=results,
            count=len(results)
        )

    async def compare_test_prices(self, request: ComparisonRequest) -> ComparisonResponse:
        try:
            result = await scraper_service.compare_prices(request.test_name)
            return ComparisonResponse(**result)
        except Exception as e:
            logger.error(f"Comparison failed: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")

scraper_controller = ScraperController()

from fastapi import APIRouter, status
from src.schemas.scraper_schemas import ScrapeRequest, ScrapeResponse, ComparisonRequest, ComparisonResponse
from src.controllers.scraper_controller import scraper_controller
from src.api import batch_routes

# Create main router
router = APIRouter()

# Include scraper routes with prefix
scraper_router = APIRouter(prefix="/api/v1/scrape", tags=["Scrapers"])

@scraper_router.post(
    "",
    response_model=ScrapeResponse,
    status_code=status.HTTP_200_OK,
    summary="Scrape lab test prices",
    description="Scrape test prices from specified lab website"
)
async def scrape_test(request: ScrapeRequest) -> ScrapeResponse:
    return await scraper_controller.scrape_test(request)

@scraper_router.post("/compare", response_model=ComparisonResponse)
async def compare_test_prices(request: ComparisonRequest) -> ComparisonResponse:
    """Compare test prices across all labs"""
    return await scraper_controller.compare_test_prices(request)

# Include all routers
router.include_router(scraper_router)
router.include_router(batch_routes.router)

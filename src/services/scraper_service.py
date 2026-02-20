import asyncio
from src.schemas.scraper_schemas import LabName, TestResult
from src.scrapers.onemg_scraper import scrape_1mg
from src.scrapers.orange_scraper import scrape_orange
from src.scrapers.redcliffe_scraper import scrape_redcliffe
from src.scrapers.lalpathlabs_scraper import scrape_lalpathlabs
from src.exceptions import ScraperException
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ScraperService:
    async def scrape_test(self, test_name: str, lab_name: LabName) -> list[TestResult]:
        logger.info(f"Starting scrape for test='{test_name}' from lab='{lab_name.value}'")
        try:
            if lab_name == LabName.ONEMG:
                results = await scrape_1mg(test_name)
            elif lab_name == LabName.ORANGE:
                results = await scrape_orange(test_name)
            elif lab_name == LabName.REDCLIFFE:
                results = await scrape_redcliffe(test_name)
            elif lab_name == LabName.LALPATHLABS:
                results = await scrape_lalpathlabs(test_name)
            else:
                raise ScraperException(f"Unsupported lab: {lab_name}")
            
            logger.info(f"Scrape completed successfully. Found {len(results)} results for '{test_name}' from '{lab_name.value}'")
            return [TestResult(**result) for result in results]
        except Exception as e:
            logger.error(f"Scraping failed for test='{test_name}' from lab='{lab_name.value}': {str(e)}", exc_info=True)
            raise ScraperException(f"Scraping failed: {str(e)}")

    async def compare_prices(self, test_name: str) -> dict:
        logger.info(f"Starting comparison for test: {test_name}")
        
        results = await asyncio.gather(
            scrape_1mg(test_name),
            scrape_orange(test_name),
            scrape_redcliffe(test_name),
            scrape_lalpathlabs(test_name),
            return_exceptions=True
        )
        
        lab_results = {
            "1mg": results[0] if not isinstance(results[0], Exception) else [],
            "orange": results[1] if not isinstance(results[1], Exception) else [],
            "redcliffe": results[2] if not isinstance(results[2], Exception) else [],
            "lalpathlabs": results[3] if not isinstance(results[3], Exception) else []
        }
        
        comparison = {
            "test_searched": test_name,
            "comparison": []
        }
        
        for lab_name, lab_data in lab_results.items():
            if lab_data and len(lab_data) > 0:
                comparison["comparison"].append({
                    "lab": lab_name,
                    "test_name": lab_data[0]["test_name"],
                    "price": lab_data[0].get("price", "N/A")
                })
            else:
                comparison["comparison"].append({
                    "lab": lab_name,
                    "test_name": "Not found",
                    "price": "N/A"
                })
        
        logger.info(f"Comparison completed for test: {test_name}")
        return comparison

scraper_service = ScraperService()

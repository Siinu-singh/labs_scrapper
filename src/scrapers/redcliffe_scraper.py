from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from src.utils.driver_utils import create_stealth_driver
from src.utils.logger import setup_logger
import time
import asyncio

logger = setup_logger(__name__)

def fuzzy_match(str1: str, str2: str, threshold: float = 0.6) -> bool:
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio() >= threshold

async def scrape_redcliffe(test_name: str) -> list[dict]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _scrape_redcliffe_sync, test_name)

def _scrape_redcliffe_sync(test_name: str) -> list[dict]:
    logger.debug(f"Starting Redcliffe scraper for test: {test_name}")
    driver = None
    try:
        logger.debug("Initializing Chrome driver")
        driver = create_stealth_driver()
        driver.get("https://redcliffelabs.com/")
        
        # Solution 3: Wait for page to fully load
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(2)
        logger.debug("Navigated to Redcliffe Labs page - fully loaded")
        
        wait = WebDriverWait(driver, 20)
        search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Search Tests']")))
        
        search_input.send_keys(test_name)
        search_input.send_keys(Keys.RETURN)
        logger.debug(f"Entered search term: {test_name}")
        
        # Solution 1: Wait for results to load
        time.sleep(2)
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='ProductCard_productCard__']"))
            )
            logger.debug("Results loaded successfully")
        except:
            logger.warning("Results slow to load, waiting longer")
            time.sleep(3)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find all product cards in results
        results_container = soup.find('div', class_=lambda x: x and 'TestsResults_testsResults__productCards__NRL8m' in x)
        if results_container:
            product_cards = results_container.find_all('div', class_=lambda x: x and 'ProductCard_outer__EmZ5x' in x)
        else:
            product_cards = soup.find_all('div', class_=lambda x: x and 'ProductCard_outer__EmZ5x' in x)
        
        logger.debug(f"Found {len(product_cards)} product cards")
        
        # Fuzzy match to find the best matching test from results
        best_match_score = 0
        best_match_test = None
        
        for card in product_cards:
            # Extract test name from the heading
            name_elem = card.find('span', class_=lambda x: x and 'ProductCard_productCard__head__heading__text__wbN8s' in x)
            if not name_elem:
                name_elem = card.find('span', class_=lambda x: x and 'ProductCard_productCard__head__heading__text' in x)
            
            if name_elem:
                # Get text and clean up (properly handle spaces between <b> tags)
                test_name_found = ' '.join(name_elem.get_text().split())
                
                # Extract offer price (discounted price)
                price_elem = card.find('span', class_=lambda x: x and 'ProductCard_packagePrice__offerPrice__OZ5sv' in x)
                if not price_elem:
                    # Fallback to main price
                    price_elem = card.find('span', class_=lambda x: x and 'ProductCard_packagePrice__mainPrice__fKjw5' in x)
                
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    
                    # Calculate match score using SequenceMatcher
                    match_score = SequenceMatcher(None, test_name.lower(), test_name_found.lower()).ratio()
                    
                    # Boost score if search term words appear in the test name
                    search_words = test_name.lower().split()
                    item_words = test_name_found.lower().split()
                    word_matches = sum(1 for word in search_words if any(word in item_word for item_word in item_words))
                    word_boost = (word_matches / len(search_words)) * 0.3 if search_words else 0
                    
                    final_score = match_score + word_boost
                    
                    logger.debug(f"Item: '{test_name_found}' - Score: {final_score:.2f} (base: {match_score:.2f}, boost: {word_boost:.2f})")
                    
                    if final_score > best_match_score:
                        best_match_score = final_score
                        best_match_test = {
                            "test_name": test_name_found,
                            "price": price_text
                        }
        
        tests = []
        if best_match_test and best_match_score >= 0.3:
            logger.info(f"Best match found with score {best_match_score:.2f}: '{best_match_test['test_name']}'")
            tests.append(best_match_test)
        elif best_match_test:
            logger.warning(f"No good match found (best score: {best_match_score:.2f}), using top result: '{best_match_test['test_name']}'")
            tests.append(best_match_test)
        
        logger.info(f"Redcliffe scraper found {len(tests)} results for '{test_name}'")
        return tests
    except Exception as e:
        logger.error(f"Error in Redcliffe scraper: {str(e)}", exc_info=True)
        return []
    finally:
        if driver:
            try:
                driver.quit()
                logger.debug("Chrome driver closed")
            except PermissionError:
                # ChromeDriver already terminated, suppress the signal error
                logger.debug("Driver terminated (signal error ignored)")
            except Exception as e:
                logger.debug(f"Driver cleanup warning (can be ignored): {str(e)}")

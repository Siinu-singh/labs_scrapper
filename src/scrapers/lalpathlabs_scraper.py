from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from src.utils.driver_utils import create_stealth_driver
from src.utils.logger import setup_logger
import asyncio
import time
import re

logger = setup_logger(__name__)

async def scrape_lalpathlabs(test_name: str) -> list[dict]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _scrape_lalpathlabs_sync, test_name)

def _scrape_lalpathlabs_sync(test_name: str) -> list[dict]:
    logger.debug(f"Starting Lal Path Labs scraper for test: {test_name}")
    driver = None
    try:
        logger.debug("Initializing Chrome driver")
        driver = create_stealth_driver()
        driver.get("https://www.lalpathlabs.com/book-a-test/delhi")
        
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(2)
        logger.debug("Navigated to Lal Path Labs page - fully loaded")
        
        wait = WebDriverWait(driver, 20)
        search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.rbt-input-main")))
        
        search_input.send_keys(test_name)
        logger.debug(f"Entered search term: {test_name}")
        
        time.sleep(1)
        try:
            dropdown = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.rbt-menu.dropdown-menu.show"))
            )
            logger.debug("Dropdown loaded successfully")
        except:
            logger.warning("Dropdown slow to load, waiting longer")
            time.sleep(2)
            dropdown = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.rbt-menu.dropdown-menu.show")))
        
        # Fuzzy match dropdown items
        best_match_item = None
        best_match_score = 0
        best_match_text = ""
        
        dropdown_items = driver.find_elements(By.CSS_SELECTOR, "a.dropdown-item")
        logger.debug(f"Found {len(dropdown_items)} dropdown items")
        
        if dropdown_items:
            for item in dropdown_items:
                item_text = item.text.strip()
                
                # Calculate match score
                match_score = SequenceMatcher(None, test_name.lower(), item_text.lower()).ratio()
                
                # Boost score if search term words are in item text
                search_words = test_name.lower().split()
                item_words = item_text.lower().split()
                word_matches = sum(1 for word in search_words if any(word in item_word for item_word in item_words))
                word_boost = (word_matches / len(search_words)) * 0.3 if search_words else 0
                
                final_score = match_score + word_boost
                
                logger.debug(f"Item: '{item_text}' - Score: {final_score:.2f} (base: {match_score:.2f}, boost: {word_boost:.2f})")
                
                if final_score > best_match_score:
                    best_match_score = final_score
                    best_match_item = item
                    best_match_text = item_text
            
            if best_match_item and best_match_score >= 0.3:
                logger.info(f"Best match found with score {best_match_score:.2f}: '{best_match_text}'")
                driver.execute_script("arguments[0].click();", best_match_item)
                logger.debug("Clicked on best matching dropdown item")
                time.sleep(3)
            elif dropdown_items:
                logger.warning(f"No good match found (best score: {best_match_score:.2f}), clicking first item")
                driver.execute_script("arguments[0].click();", dropdown_items[0])
                logger.debug("Clicked on first dropdown item")
                time.sleep(3)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        product_details = soup.find('div', class_='productDetails')
        
        if product_details:
            test_name_elem = product_details.find('h1', class_='productName')
            price_elem = product_details.find('span', class_='updated-price')
            
            if test_name_elem and price_elem:
                test_name_found = test_name_elem.get_text(strip=True)
                price_text = price_elem.get_text(strip=True)
                
                price_match = re.search(r'₹?\s*(\d+)', price_text)
                if price_match:
                    price = f"₹{price_match.group(1)}"
                else:
                    price = price_text
                
                tests = [{
                    "test_name": test_name_found,
                    "price": price
                }]
            else:
                tests = []
        else:
            tests = []
        
        logger.info(f"Lal Path Labs scraper found {len(tests)} results for '{test_name}'")
        return tests
    except Exception as e:
        logger.error(f"Error in Lal Path Labs scraper: {str(e)}", exc_info=True)
        return []
    finally:
        if driver:
            try:
                driver.quit()
                logger.debug("Chrome driver closed")
            except Exception as e:
                logger.debug(f"Driver cleanup warning (can be ignored): {str(e)}")

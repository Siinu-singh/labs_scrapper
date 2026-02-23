from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from src.utils.driver_utils import create_stealth_driver
from src.utils.logger import setup_logger
import asyncio
import time
import re

logger = setup_logger(__name__)

def fuzzy_match(str1: str, str2: str, threshold: float = 0.6) -> bool:
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio() >= threshold

async def scrape_1mg(test_name: str) -> list[dict]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _scrape_1mg_sync, test_name)

def _scrape_1mg_sync(test_name: str) -> list[dict]:
    logger.debug(f"Starting 1mg scraper for test: {test_name}")
    driver = None
    try:
        driver = create_stealth_driver()
        driver.get("https://www.1mg.com/labs")
        
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(2)
        logger.debug("Navigated to 1mg labs page - fully loaded")
        
        wait = WebDriverWait(driver, 20)
        search_box = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='Search tests or full body checkups']")))
        
        search_box.click()
        search_box.clear()
        search_box.send_keys(test_name)
        logger.debug(f"Entered search term: {test_name}")
        
        time.sleep(1)
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".TestRedirection__itemWrapper__Yv_86"))
            )
            logger.debug("Suggestions loaded successfully")
        except:
            logger.warning("Suggestions slow to load, waiting longer")
            time.sleep(2)
        
        # Fuzzy match dropdown items using aria-label
        best_match_item = None
        best_match_score = 0
        best_match_text = ""
        
        try:
            test_items = driver.find_elements(By.CSS_SELECTOR, ".TestRedirection__itemWrapper__Yv_86")
            logger.debug(f"Found {len(test_items)} dropdown items")
            
            if test_items:
                for item in test_items:
                    # Get text from aria-label attribute (more reliable)
                    item_text = item.get_attribute("aria-label") or item.text.strip()
                    
                    # Calculate match score
                    match_score = SequenceMatcher(None, test_name.lower(), item_text.lower()).ratio()
                    
                    # Boost score if search term words are in item text
                    search_words = test_name.lower().split()
                    item_words = item_text.lower().split()
                    word_matches = sum(1 for word in search_words if any(word in item_word for item_word in item_words))
                    word_boost = (word_matches / len(search_words)) * 0.3
                    
                    final_score = match_score + word_boost
                    
                    logger.debug(f"Item: '{item_text}' - Score: {final_score:.2f} (base: {match_score:.2f}, boost: {word_boost:.2f})")
                    
                    if final_score > best_match_score:
                        best_match_score = final_score
                        best_match_item = item
                        best_match_text = item_text
                
                if best_match_item and best_match_score >= 0.3:
                    logger.info(f"Best match found with score {best_match_score:.2f}: '{best_match_text}'")
                    driver.execute_script("arguments[0].click();", best_match_item)
                    logger.debug("Clicked on best matching test item")
                    time.sleep(5)
                else:
                    logger.warning(f"No good match found (best score: {best_match_score:.2f}), clicking first item")
                    driver.execute_script("arguments[0].click();", test_items[0])
                    time.sleep(5)
        except Exception as e:
            logger.warning(f"Error in dropdown selection: {str(e)}")
            search_box.send_keys(Keys.RETURN)
            logger.debug("Pressed Enter on search box")
            time.sleep(5)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        tests = []
        
        test_name_h1 = soup.find('h1')
        if test_name_h1:
            current_test_name = test_name_h1.get_text().strip()
            price_elements = soup.find_all('div', class_='headingSmallBold')
            
            for price_elem in price_elements:
                price_text = price_elem.get_text().strip()
                if '₹' in price_text and re.search(r'\d', price_text):
                    tests.append({
                        "test_name": current_test_name,
                        "price": price_text
                    })
                    break
        
        logger.info(f"1mg scraper found {len(tests)} results for '{test_name}'")
        return tests
    except Exception as e:
        logger.error(f"Error in 1mg scraper: {str(e)}", exc_info=True)
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

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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

def fuzzy_match(str1: str, str2: str, threshold: float = 0.6) -> bool:
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio() >= threshold

async def scrape_orange(test_name: str) -> list[dict]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _scrape_orange_sync, test_name)

def _scrape_orange_sync(test_name: str) -> list[dict]:
    
    logger.debug(f"Starting Orange Health scraper for test: {test_name}")
    driver = None
    try:
        logger.debug("Initializing Chrome driver")
        driver = create_stealth_driver()
        driver.get("https://orangehealth.in/")
        
        # Solution 3: Wait for page to fully load
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(2)
        logger.debug("Navigated to Orange Health page - fully loaded")

        wait = WebDriverWait(driver, 20)

        # Wait for and click fake search
        search_elements = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".fake-search-input"))
        )
        if search_elements:
            driver.execute_script("arguments[0].click();", search_elements[0])
            logger.debug("Clicked fake search input")
            
            # Solution 1: Wait for modal to fully load
            time.sleep(1)
            try:
                WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
                )
                logger.debug("Modal loaded successfully")
            except:
                logger.warning("Modal slow to load, waiting longer")
                time.sleep(3)

        # Wait for real input to be visible and interactable
        try:
            search_input = WebDriverWait(driver, 25).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='text']"))
            )
            search_input.send_keys(test_name)
            search_input.send_keys(Keys.RETURN)
            logger.debug(f"Entered search term: {test_name}")

            # Wait for results to load
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "article.test-card-container")
                )
            )
            time.sleep(2)

        except Exception as e:
            logger.warning(
                f"Search input not found or results didn't load: {str(e)}"
            )
            return []

        soup = BeautifulSoup(driver.page_source, "html.parser")

        test_cards = soup.find_all("article", class_="test-card-container")
        logger.debug(f"Found {len(test_cards)} test cards")

        # Fuzzy match to find the best matching test from results
        best_match_score = 0
        best_match_test = None

        for card in test_cards:
            name_element = card.find("h3")
            if name_element:
                test_name_found = name_element.get_text().strip()
                real_price_elem = card.find(
                    "span", class_=lambda x: x and "real-price" in x
                )

                if real_price_elem:
                    price_text = real_price_elem.get_text().strip()
                    price_numbers = re.sub(r"[^\d]", "", price_text)
                    if price_numbers:
                        price = f"₹{price_numbers}"
                        
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
                                "price": price
                            }

        tests = []
        if best_match_test and best_match_score >= 0.3:
            logger.info(f"Best match found with score {best_match_score:.2f}: '{best_match_test['test_name']}'")
            tests.append(best_match_test)
        elif best_match_test:
            logger.warning(f"No good match found (best score: {best_match_score:.2f}), using top result: '{best_match_test['test_name']}'")
            tests.append(best_match_test)

        logger.info(
            f"Orange Health scraper found {len(tests)} results for '{test_name}'"
        )
        return tests

    except Exception as e:
        logger.error(f"Error in Orange Health scraper: {str(e)}", exc_info=True)
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

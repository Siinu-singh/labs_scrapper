from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from src.utils.logger import setup_logger
import random
import logging

logger = setup_logger(__name__)

# Suppress Selenium service process errors (PermissionError from chromedriver cleanup)
logging.getLogger('selenium.webdriver.common.service').setLevel(logging.CRITICAL)
logging.getLogger('selenium.webdriver.chrome.service').setLevel(logging.CRITICAL)

def create_stealth_driver():
    """Create undetectable Chrome driver that mimics real user browser"""
    chrome_options = Options()
    
    # Essential arguments only - remove suspicious flags
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--disable-extensions")
    
    # Realistic user agent
    chrome_version = random.randint(120, 131)
    chrome_options.add_argument(f"--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version}.0.0.0 Safari/537.36")
    
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    })
    chrome_options.binary_location = "/usr/bin/chromium-browser"
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # Inject stealth JavaScript
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        
        Object.defineProperty(navigator, 'plugins', {
            get: () => [
                {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format'},
                {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: ''},
                {name: 'Native Client', filename: 'internal-nacl-plugin', description: ''}
            ]
        });
        
        Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        Object.defineProperty(navigator, 'vendor', {get: () => 'Google Inc.'});
        Object.defineProperty(navigator, 'platform', {get: () => 'Linux x86_64'});
        Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
        Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
        
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {}
        };
        
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({state: Notification.permission}) :
                originalQuery(parameters)
        );
        
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) return 'Intel Inc.';
            if (parameter === 37446) return 'Intel Iris OpenGL Engine';
            return getParameter.call(this, parameter);
        };
        
        ['cdc_adoQpoasnfa76pfcZLmcfl_Array', 'cdc_adoQpoasnfa76pfcZLmcfl_Promise', 'cdc_adoQpoasnfa76pfcZLmcfl_Symbol'].forEach(prop => delete window[prop]);
        """
    })
    
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {
        "userAgent": driver.execute_script("return navigator.userAgent"),
        "platform": "Linux x86_64",
        "acceptLanguage": "en-US,en;q=0.9"
    })
    
    driver.execute_cdp_cmd("Emulation.setTimezoneOverride", {"timezoneId": "America/New_York"})
    
    logger.debug("Stealth Chrome driver initialized")
    return driver

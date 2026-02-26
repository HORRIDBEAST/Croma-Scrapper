import time
import redis
import json
import logging
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_croma_data(url):
    """
    Enhanced scraper with better lazy loading handling for Croma website.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = None
    
    try:
        logging.info("Initializing Selenium WebDriver...")
        driver = webdriver.Chrome(service=service, options=options)
        
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logging.info(f"Requesting page with Selenium: {url}")
        driver.get(url)

        logging.info("Waiting for initial product items to be visible...")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "product-item"))
        )
        
        time.sleep(3)
        
        logging.info("Starting enhanced scrolling to trigger lazy loading...")
        
        total_height = driver.execute_script("return document.body.scrollHeight")
        current_position = 0
        scroll_increment = 300 
        
        while current_position < total_height:
            driver.execute_script(f"window.scrollTo(0, {current_position});")
            time.sleep(0.5)  
            current_position += scroll_increment
            
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height > total_height:
                total_height = new_height
        
        # Method 2: Scroll to each product individually
        logging.info("Scrolling to individual products to ensure image loading...")
        try:
            product_items = driver.find_elements(By.CLASS_NAME, "product-item")
            logging.info(f"Found {len(product_items)} products to scroll through")
            
            for i, item in enumerate(product_items):
                try:
                    # Scroll to the product
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", item)
                    time.sleep(0.8)  # Wait for image to load
                    
                    # Additional trigger for lazy loading
                    ActionChains(driver).move_to_element(item).perform()
                    time.sleep(0.3)
                    
                    if i % 5 == 0:
                        logging.info(f"Processed {i+1}/{len(product_items)} products")
                        
                except Exception as e:
                    logging.debug(f"Error scrolling to product {i}: {e}")
                    continue
        except Exception as e:
            logging.error(f"Error during individual product scrolling: {e}")
        
        # Method 3: Force trigger lazy loading with JavaScript
        logging.info("Force triggering lazy loading with JavaScript...")
        driver.execute_script("""
            // Trigger intersection observer for all images
            var images = document.querySelectorAll('img[data-src], img[loading="lazy"], img[data-lazy-src]');
            images.forEach(function(img, index) {
                // Scroll into view
                img.scrollIntoView({behavior: 'auto', block: 'center'});
                
                // Trigger various lazy loading events
                var events = ['scroll', 'resize', 'orientationchange', 'touchstart', 'touchmove'];
                events.forEach(function(eventType) {
                    var event = new Event(eventType);
                    window.dispatchEvent(event);
                });
                
                // Force load data-src images
                if (img.dataset.src && !img.src.includes('lazyLoading.gif')) {
                    img.src = img.dataset.src;
                }
                if (img.dataset.lazySrc && !img.src.includes('lazyLoading.gif')) {
                    img.src = img.dataset.lazySrc;
                }
            });
        """)
        
        # Wait for images to load after JavaScript execution
        time.sleep(5)
        
        # Final comprehensive scroll
        logging.info("Performing final comprehensive scroll...")
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        # Wait for any remaining images to load
        logging.info("Waiting for final image loads...")
        WebDriverWait(driver, 10).until(
            lambda d: len(d.find_elements(By.XPATH, "//img[contains(@src, 'lazyLoading.gif')]")) < 5
        )
        
        # Get final HTML
        logging.info("Getting final page source after all scrolling.")
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')

        # Enhanced Product Scraping
        products = []
        product_list_items = soup.find_all('li', class_='product-item')
        
        if product_list_items:
            logging.info(f"Found {len(product_list_items)} product items for scraping.")
            
            for i, item in enumerate(product_list_items):
                product = {}
                
                # Extract title
                title_element = item.find('h3', class_='product-title')
                product['title'] = title_element.text.strip() if title_element else 'N/A'
                
                # Extract prices
                prices = item.find_all('span', class_='amount')
                if len(prices) > 1:
                    product['sale_price'] = prices[0].text.strip()
                    product['price'] = prices[1].text.strip()
                elif prices:
                    product['sale_price'] = prices[0].text.strip()
                    product['price'] = ''
                else:
                    product['sale_price'] = 'N/A'
                    product['price'] = 'N/A'

                # Enhanced image extraction
                product['image_url'] = ''
                img_tags = item.find_all('img')

                # Priority order for image attributes
                image_attrs = ['src', 'data-src', 'data-lazy-src', 'data-original', 'data-srcset']
                
                for img in img_tags:
                    for attr in image_attrs:
                        image_url = img.get(attr)
                        if image_url and not image_url.endswith('lazyLoading.gif'):
                            if image_url.startswith('http') or image_url.startswith('//'):
                                product['image_url'] = image_url
                                break
                    if product['image_url']:
                        break

                # Fallback selectors if no image found
                if not product['image_url']:
                    selectors = [
                        'img.product-img', 
                        '.product-image img', 
                        'figure img', 
                        'a img',
                        '.product-img-wrapper img',
                        '.image-container img'
                    ]
                    
                    for selector in selectors:
                        img_element = item.select_one(selector)
                        if img_element:
                            for attr in image_attrs:
                                image_url = img_element.get(attr)
                                if image_url and not image_url.endswith('lazyLoading.gif'):
                                    if image_url.startswith('http') or image_url.startswith('//'):
                                        product['image_url'] = image_url
                                        break
                        if product['image_url']:
                            break

                # Final fallback
                if not product['image_url'] or product['image_url'].endswith('lazyLoading.gif'):
                    product['image_url'] = 'https://via.placeholder.com/400x400?text=No+Image'
                    logging.warning(f"No valid image found for product {i+1}: {product['title']}")
                
                products.append(product)
                
                # Log progress every 5 products
                if (i + 1) % 5 == 0:
                    logging.info(f"Scraped {i+1}/{len(product_list_items)} products")
        else:
            logging.warning("No product items found.")

        # Page Elements
        head_element = soup.find('head')
        header_element = soup.find('header', id='header')
        
        page_elements = {
            "head": str(head_element) if head_element else None,
            "header": str(header_element) if header_element else None,
        }
        
        # Log final statistics
        valid_images = sum(1 for p in products if p['image_url'] and not p['image_url'].endswith('placeholder'))
        logging.info(f"Scraping completed: {len(products)} products, {valid_images} with valid images")
        
        return products, page_elements

    except Exception as e:
        logging.error(f"Error during scraping: {e}")
        return [], {"head": None, "header": None}
    finally:
        if driver:
            driver.quit()

def store_in_redis(redis_client, key, data):
    """Generic function to store data in Redis."""
    try:
        redis_client.set(key, json.dumps(data))
        logging.info(f"Data successfully stored in Redis with key '{key}'.")
    except Exception as e:
        logging.error(f"Failed to store data for key '{key}': {e}")

if __name__ == "__main__":
    croma_url = "https://www.croma.com/televisions-accessories/c/997"
    product_data, page_element_data = scrape_croma_data(croma_url)
    
    try:
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        r.ping()
        
        if product_data:
            store_in_redis(r, "croma_products", product_data)
            
            # Log image statistics
            valid_images = sum(1 for p in product_data if p['image_url'] and not p['image_url'].endswith('placeholder'))
            logging.info(f"Final results: {len(product_data)} products, {valid_images} with valid images")
        else:
            logging.warning("No product data was scraped.")
            
        if page_element_data.get("head") or page_element_data.get("header"):
            store_in_redis(r, "croma_page_elements", page_element_data)
        else:
            logging.warning("No head/header data was scraped.")

    except redis.ConnectionError:
        logging.error("Could not connect to Redis. Is the server running?")
        
    logging.info("Scraping script finished.")
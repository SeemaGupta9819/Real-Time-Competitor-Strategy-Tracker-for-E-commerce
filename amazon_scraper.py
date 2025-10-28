from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import random

def clean_text(text):
    return text.strip().replace('\n', ' ').replace('\xa0', ' ') if text else ""

def get_headers():
    """Return randomized headers to avoid detection"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
    ]
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://www.amazon.in/',
        'DNT': '1'
    }

def setup_driver():
    """Setup Chrome driver with anti-detection options"""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    
    # Randomize user agent
    options.add_argument(f"user-agent={get_headers()['User-Agent']}")
    
    driver = webdriver.Chrome(options=options)
    
    # Override navigator.webdriver flag
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def get_html_with_selenium(driver, url, wait_time=3):
    """Use Selenium instead of requests for better success rate"""
    try:
        driver.get(url)
        time.sleep(random.uniform(wait_time, wait_time + 2))
        return driver.page_source
    except Exception as e:
        print(f"Error fetching URL with Selenium: {e}")
        return None

def extract_product_fields(product_div):
    title_elem = product_div.find("span", class_="a-size-medium a-color-base a-text-normal") \
        or product_div.find("h2") \
        or product_div.get('aria-label', None)
    product_name = clean_text(title_elem.text if hasattr(title_elem, "text") else title_elem)
    asin = product_div.get('data-asin', '')
    brand = product_name.split(" ")[0] if product_name else ""
    price_tag = product_div.select_one("span.a-price > span.a-offscreen") or product_div.find("span", class_="a-price-whole")
    price = price_tag.text.strip().replace('₹', '').replace(',', '') if price_tag else ""
    mrp_tag = product_div.select_one("span.a-price.a-text-price > span.a-offscreen")
    mrp = mrp_tag.text.strip().replace('₹', '').replace(',', '') if mrp_tag else ""
    discount = ""
    for span in product_div.select("span"):
        txt = span.get_text(strip=True)
        if "%" in txt and "off" in txt.lower():
            discount = txt
            break
    stock_status = "In Stock"
    if product_div.find(string=lambda t: t and "out of stock" in t.lower()):
        stock_status = "Out of Stock"
    rating_tag = product_div.find("span", class_="a-icon-alt")
    rating = rating_tag.text.strip().split(" ")[0] if rating_tag else ""
    reviews_tag = product_div.select_one("span.s-underline-text") or product_div.select_one("span.a-size-base")
    reviews = ''.join(filter(str.isdigit, reviews_tag.text.strip())) if reviews_tag and reviews_tag.text else ""
    link_elem = product_div.find('a', class_='a-link-normal s-no-outline') or product_div.find('a', href=lambda x: x and '/dp/' in x)
    if link_elem and link_elem.get('href'):
        href = link_elem['href']
        product_link = href if href.startswith('http') else f"https://www.amazon.in{href}"
    else:
        product_link = ""
    base_link = product_link.split('?')[0].split('/ref')[0] if product_link else ""
    reviews_link = f"{base_link}#customerReviews" if product_link else ""
    scraped_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return {
        "Product_Name": product_name,
        "Product_ASIN": asin,
        "Brand": brand,
        "Price": price,
        "MRP": mrp,
        "Discount": discount,
        "Stock_Status": stock_status,
        "Rating": rating,
        "Reviews": reviews,
        "Seller": "",
        "Product_Link": product_link,
        "Reviews_Link": reviews_link,
        "Scraped_At": scraped_at
    }

def extract_seller(soup):
    seller_elem = soup.select_one("a#sellerProfileTriggerId") or soup.select_one("div#merchant-info")
    if seller_elem:
        return clean_text(seller_elem.text)
    return ""

def extract_all_reviews_selenium(driver, reviews_url, max_pages=10):
    all_reviews = []
    page_num = 1
    while page_num <= max_pages:
        try:
            driver.get(reviews_url)
            time.sleep(random.uniform(2, 4))
            soup = BeautifulSoup(driver.page_source, "lxml")
            review_blocks = soup.select("div[data-hook='review']")
            if not review_blocks:
                break
            for block in review_blocks:
                rev_title = block.select_one("a[data-hook='review-title']")
                rev_body = block.select_one("span[data-hook='review-body']")
                rev_star = block.select_one("i[data-hook='review-star-rating']")
                title = clean_text(rev_title.text) if rev_title else ""
                body = clean_text(rev_body.text) if rev_body else ""
                stars = clean_text(rev_star.text.split(" ")[0]) if rev_star else ""
                all_reviews.append({'title': title, 'body': body, 'stars': stars})
            next_button = driver.find_elements(By.CSS_SELECTOR, "li.a-last a")
            if not next_button:
                break
            reviews_url = next_button[0].get_attribute('href')
            page_num += 1
            time.sleep(random.uniform(1, 3))
        except Exception as e:
            print(f"Error extracting reviews on page {page_num}: {e}")
            break
    return all_reviews

def main(query, pages=1, max_review_pages=3):
    driver = setup_driver()
    base_url = f"https://www.amazon.in/s?k={query}"
    final_data = []
    
    try:
        for page in range(1, pages + 1):
            url = f"{base_url}&page={page}"
            print(f"\nScraping Search Page {page}: {url}")
            
            # Use Selenium for search page too
            html = get_html_with_selenium(driver, url)
            if not html:
                print("Failed to fetch search page")
                continue
            
            soup = BeautifulSoup(html, "lxml")
            products = soup.find_all('div', {'data-component-type': 's-search-result', 'data-asin': True})
            print(f"Products Found: {len(products)}")
            
            for idx, product in enumerate(products, 1):
                pdict = extract_product_fields(product)
                if not pdict["Product_ASIN"]:
                    continue
                
                print(f"---\n[{idx}/{len(products)}] Processing: {pdict['Product_Name'][:50]}...")
                
                # Get seller from product page
                if pdict["Product_Link"]:
                    detail_html = get_html_with_selenium(driver, pdict["Product_Link"], wait_time=2)
                    if detail_html:
                        detail_soup = BeautifulSoup(detail_html, 'lxml')
                        pdict["Seller"] = extract_seller(detail_soup)
                
                # Extract reviews
                reviews_url = f"https://www.amazon.in/product-reviews/{pdict['Product_ASIN']}?pageNumber=1"
                all_revs = extract_all_reviews_selenium(driver, reviews_url, max_pages=max_review_pages)
                
                if all_revs:
                    for rev in all_revs:
                        row = pdict.copy()
                        row["Review_Title"] = rev["title"]
                        row["Review_Body"] = rev["body"]
                        row["Review_Stars"] = rev["stars"]
                        final_data.append(row)
                else:
                    row = pdict.copy()
                    row["Review_Title"] = ""
                    row["Review_Body"] = ""
                    row["Review_Stars"] = ""
                    final_data.append(row)
                
                # Random delay between products
                time.sleep(random.uniform(2, 4))
    
    finally:
        driver.quit()
    
    df = pd.DataFrame(final_data)
    excel_filename = f"amazon_{query.replace('+','_')}.xlsx"
    df.to_excel(excel_filename, index=False)
    print(f"\n✓ All data saved to: {excel_filename}")
    print(f"Total rows: {len(df)}")

if __name__ == "__main__":
    main("mobile+phones", pages=1, max_review_pages=3)
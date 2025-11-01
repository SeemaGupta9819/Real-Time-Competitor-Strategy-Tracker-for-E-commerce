import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import random

def clean_text(text):
    return ' '.join(text.strip().split()) if text else None

def setup_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def extract_product_fields(product_div):
    title_elem = product_div.find("span", class_="a-size-medium a-color-base a-text-normal") or product_div.find("h2")
    product_name = clean_text(title_elem.text) if title_elem else None
    asin = product_div.get('data-asin', '')
    brand = product_name.split(" ")[0] if product_name else None
    
    price_tag = product_div.select_one("span.a-price > span.a-offscreen") or product_div.find("span", class_="a-price-whole")
    price = price_tag.text.strip().replace('₹', '').replace(',', '').replace('.00', '') if price_tag else None
    
    mrp_tag = product_div.select_one("span.a-price.a-text-price > span.a-offscreen")
    mrp = mrp_tag.text.strip().replace('₹', '').replace(',', '') if mrp_tag else price
    
    discount = ""
    html_text = str(product_div)
    
    match = re.search(r'(\d+% ?off|\(\d+%\))', html_text, re.IGNORECASE)
    if match:
        discount = match.group(1)
    else:
        discount = "No Discount"
    rating_tag = product_div.find("span", class_="a-icon-alt")
    rating = rating_tag.text.strip().split(" ")[0] if rating_tag else None
    
    reviews_tag = product_div.find("span", class_="a-size-base s-underline-text")
    reviews = ''.join(filter(str.isdigit, reviews_tag.text)) if reviews_tag else None
    
    link_elem = product_div.find('a', class_='a-link-normal s-no-outline') or product_div.find('a', href=lambda x: x and '/dp/' in x)
    product_link = ""
    if link_elem and link_elem.get('href'):
        href = link_elem['href']
        product_link = href if href.startswith('http') else f"https://www.amazon.in{href}"
    
    return {
        "Product_Name": product_name,
        "Product_ASIN": asin,
        "Brand": brand,
        "Price": price,
        "MRP": mrp,
        "Discount": discount,
        "Rating": rating,
        "Product_Link": product_link,
        "Scraped_At": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def extract_reviews_from_product_page(driver, product_url, max_reviews=10):
    all_reviews = []
    if not product_url:
        return all_reviews
    
    try:
        driver.get(product_url)
        time.sleep(random.uniform(3, 5))
        
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 1000)")
            time.sleep(1)
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        review_blocks = soup.select("div[data-hook='review']")
        
        if not review_blocks:
            review_blocks = soup.find_all("div", {"class": "a-section review aok-relative"})
        if not review_blocks:
            review_blocks = soup.find_all("div", id=lambda x: x and "customer_review" in str(x))
        
        for block in review_blocks[:max_reviews]:
            reviewer_tag = block.find("span", class_="a-profile-name")
            title_tag = block.find("a", {"data-hook": "review-title"}) or block.find("span", {"data-hook": "review-title"})
            body_tag = block.find("span", {"data-hook": "review-body"})
            stars_tag = block.find("i", {"data-hook": "review-star-rating"}) or block.find("span", class_="a-icon-alt")
            date_tag = block.find("span", {"data-hook": "review-date"})
            
            stars = ""
            if stars_tag:
                stars_text = stars_tag.text.strip()
                stars = stars_text.split()[0] if stars_text else None
            total_reviews_text = soup.select_one("span[data-hook='total-review-count']") or \
                     soup.find("span", class_="a-size-base a-color-secondary totalReviewCount")

            if total_reviews_text:
                total_reviews = ''.join(filter(str.isdigit, total_reviews_text.text))
            else:
                total_reviews = "Not found"
            all_reviews.append({
                "total_review": total_reviews,
                "title": clean_text(title_tag.text) if title_tag else None,
                "body": clean_text(body_tag.text) if body_tag else None,
                "stars": stars,
                "reviewer": clean_text(reviewer_tag.text) if reviewer_tag else None,
                "date": clean_text(date_tag.text) if date_tag else None
            })
        
    except Exception as e:
        print(f"Error extracting reviews: {e}")
    
    return all_reviews

def main(query, pages=1, max_reviews_per_product=5):
    driver = setup_driver()
    base_url = f"https://www.amazon.in/s?k={query}"
    final_data = []
    
    try:
        for page in range(1, pages + 1):
            url = f"{base_url}&page={page}"
            print(f"\nScraping Page {page}: {url}")
            
            driver.get(url)
            time.sleep(random.uniform(4, 6))
            
            soup = BeautifulSoup(driver.page_source, "html.parser")
            products = soup.find_all('div', {'data-component-type': 's-search-result', 'data-asin': True})
            print(f"Found {len(products)} products")
            
            for idx, product in enumerate(products, 1):
                pdict = extract_product_fields(product)
                
                if not pdict["Product_ASIN"] or not pdict["Product_Link"]:
                    continue
                
                print(f"[{idx}/{len(products)}] {pdict['Product_Name'][:50]}...")
                
                all_revs = extract_reviews_from_product_page(driver, pdict['Product_Link'], max_reviews=max_reviews_per_product)
                
                if all_revs:
                    print(f"  Found {len(all_revs)} reviews")
                    for rev in all_revs:
                        row = pdict.copy()
                        row.update({
                            "Review Counting": rev['total_review'],
                            "Review_Title": rev["title"],
                            "Review_Body": rev["body"],
                            "Review_Stars": rev["stars"],
                            "Reviewer": rev["reviewer"],
                            "Review_Date": rev["date"]
                        })
                        final_data.append(row)
                else:
                    row = pdict.copy()
                    row.update({"Review_Title": "", "Review_Body": "", "Review_Stars": "", "Reviewer": "", "Review_Date": ""})
                    final_data.append(row)
                
                time.sleep(random.uniform(3, 5))
                
    finally:
        driver.quit()
    
    df = pd.DataFrame(final_data)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    excel_filename = f"amazon_{query.replace('+','_')}_{timestamp}.xlsx"
    df.to_excel(excel_filename, index=False)
    print(f"\nCompleted! Total rows: {len(df)}, Saved to: {excel_filename}")

if __name__ == "__main__":
    main("mobile+phones", pages=1, max_reviews_per_product=5)

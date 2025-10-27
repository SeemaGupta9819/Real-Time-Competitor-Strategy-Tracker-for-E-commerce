# ---------- INSTALL DEPENDENCIES ----------
# pip install selenium beautifulsoup4 pandas

import time
import pandas as pd
import selenium 

import bs4
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime

# ---------- CONFIG ----------
SEARCH_URL = "https://www.amazon.in/s?k=mobile+phones"
HEADLESS = True
OUTPUT_FILE = "amazon_mobile_data.csv"
# -----------------------------------------

# ---------- SETUP SELENIUM ----------
options = Options()
if HEADLESS:
    options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

driver = webdriver.Chrome(options=options)
driver.get(SEARCH_URL)
time.sleep(3)  # wait for page to load

# ---------- SCROLL DOWN TO LOAD PRODUCTS ----------
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(2)

# ---------- PARSE PAGE ----------
soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

# ---------- SCRAPE DATA ----------
products = []

for item in soup.find_all("div", {"data-component-type": "s-search-result"}):
    try:
        product_name = item.h2.text.strip() if item.h2 else None
        product_asin = item.get("data-asin")
        brand = product_name.split()[0] if product_name else None
        
        # Product links
        link_tag = item.h2.a if item.h2 and item.h2.a else None
        product_link = "https://www.amazon.in" + link_tag["href"] if link_tag else None
        reviews_link = product_link + "#customerReviews" if product_link else None

        # Prices
        price_whole = item.select_one("span.a-price-whole")
        price_fraction = item.select_one("span.a-price-fraction")
        price = None
        if price_whole:
            price = price_whole.text.strip()
            if price_fraction:
                price += price_fraction.text.strip()

        mrp_tag = item.select_one("span.a-price.a-text-price span.a-offscreen")
        mrp = mrp_tag.text.strip() if mrp_tag else None

        # Discount
        discount_tag = item.select_one("span.a-letter-space + span.a-color-price")
        discount = discount_tag.text.strip() if discount_tag else None

        # Rating and Reviews
        rating_tag = item.select_one("span.a-icon-alt")
        rating = rating_tag.text.strip() if rating_tag else None
        reviews_tag = item.select_one("span.a-size-base.s-underline-text")
        reviews = reviews_tag.text.strip() if reviews_tag else None

        # Seller and Stock
        seller = "Amazon.in"  # Usually not available directly on list page
        stock_status = "Available" if "Currently unavailable" not in item.text else "Out of Stock"

        # Timestamp
        scraped_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        products.append({
            "Product_Name": product_name,
            "Product_ASIN": product_asin,
            "Brand": brand,
            "Price": price,
            "MRP": mrp,
            "Discount": discount,
            "Stock_Status": stock_status,
            "Rating": rating,
            "Reviews": reviews,
            "Seller": seller,
            "Product_Link": product_link,
            "Reviews_Link": reviews_link,
            "Scraped_At": scraped_at
        })
    except Exception as e:
        continue

# ---------- SAVE TO CSV ----------
df = pd.DataFrame(products)
df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
print(f"✅ Scraped {len(df)} products. Data saved to '{OUTPUT_FILE}'.")
print(df.head())

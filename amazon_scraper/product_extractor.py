import re
from bs4 import BeautifulSoup
from datetime import datetime
from .utils import clean_text

def extract_product_fields(product_div):
    title_elem = product_div.find("span", class_="a-size-medium a-color-base a-text-normal") or product_div.find("h2")
    product_name = clean_text(title_elem.text) if title_elem else None
    asin = product_div.get('data-asin', '')
    brand = product_name.split(" ")[0] if product_name else None

    price_tag = product_div.select_one("span.a-price > span.a-offscreen") or product_div.find("span", class_="a-price-whole")
    price = price_tag.text.strip().replace('₹', '').replace(',', '').replace('.00', '') if price_tag else None

    mrp_tag = product_div.select_one("span.a-price.a-text-price > span.a-offscreen")
    mrp = mrp_tag.text.strip().replace('₹', '').replace(',', '') if mrp_tag else price

    match = re.search(r'(\d+% ?off|\(\d+%\))', str(product_div), re.IGNORECASE)
    discount = match.group(1) if match else "No Discount"

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

import sys
sys.stdout.reconfigure(encoding='utf-8')
from bs4 import BeautifulSoup
from .driver_setup import setup_driver
from .product_extractor import extract_product_fields
from .review_extractor import extract_reviews_from_product_page
from .data_handler import save_to_excel
from .utils import human_delay

def main(query, pages=1, max_reviews_per_product=5):
    driver = setup_driver()
    base_url = f"https://www.amazon.in/s?k={query}"
    final_data = []

    try:
        for page in range(1, pages + 1):
            url = f"{base_url}&page={page}"
            print(f"\n📄 Scraping Page {page}: {url}")
            driver.get(url)
            human_delay(4, 6)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            products = soup.find_all('div', {'data-component-type': 's-search-result', 'data-asin': True})
            print(f"Found {len(products)} products")

            for idx, product in enumerate(products, 1):
                pdict = extract_product_fields(product)
                if not pdict["Product_ASIN"] or not pdict["Product_Link"]:
                    continue

                print(f"[{idx}/{len(products)}] {pdict['Product_Name'][:50]}...")
                reviews = extract_reviews_from_product_page(driver, pdict['Product_Link'], max_reviews=max_reviews_per_product)

                if reviews:
                    for rev in reviews:
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

                human_delay(3, 5)

    finally:
        driver.quit()

    save_to_excel(final_data, query)

if __name__ == "__main__":
    main("mobile+phones", pages=1, max_reviews_per_product=5)

from bs4 import BeautifulSoup
from .utils import clean_text, human_delay

def extract_reviews_from_product_page(driver, product_url, max_reviews=10):
    all_reviews = []
    if not product_url:
        return all_reviews

    try:
        driver.get(product_url)
        human_delay(3, 5)
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 1000)")
            human_delay(1, 2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        review_blocks = soup.select("div[data-hook='review']") or \
                        soup.find_all("div", {"class": "a-section review aok-relative"}) or \
                        soup.find_all("div", id=lambda x: x and "customer_review" in str(x))

        for block in review_blocks[:max_reviews]:
            reviewer_tag = block.find("span", class_="a-profile-name")
            title_tag = block.find("a", {"data-hook": "review-title"}) or block.find("span", {"data-hook": "review-title"})
            body_tag = block.find("span", {"data-hook": "review-body"})
            stars_tag = block.find("i", {"data-hook": "review-star-rating"}) or block.find("span", class_="a-icon-alt")
            date_tag = block.find("span", {"data-hook": "review-date"})
            stars = stars_tag.text.strip().split()[0] if stars_tag else None

            total_reviews_text = soup.select_one("span[data-hook='total-review-count']")
            total_reviews = ''.join(filter(str.isdigit, total_reviews_text.text)) if total_reviews_text else "Not found"

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

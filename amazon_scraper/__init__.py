"""
Amazon Scraper Package

Modular scraper for extracting product and review data from Amazon India.
"""

from .driver_setup import setup_driver
from .product_extractor import extract_product_fields
from .review_extractor import extract_reviews_from_product_page
from .data_handler import save_to_excel
from .utils import clean_text, human_delay

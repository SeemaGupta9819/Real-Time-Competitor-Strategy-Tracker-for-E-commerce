import time
import random

def clean_text(text):
    return ' '.join(text.strip().split()) if text else None

def human_delay(min_t=2.5, max_t=5.5):
    """Simulates human-like delay to reduce blocking risk."""
    time.sleep(random.uniform(min_t, max_t))

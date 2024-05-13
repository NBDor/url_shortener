import os
from .constants import SHORTCODE_MAX

GENERATE_SHORT_URL_LENGTH: int = int(os.getenv("GENERATE_SHORT_URL_LENGTH", 6))
MAX_EXECUTION_TIME: int = int(os.getenv("MAX_EXECUTION_TIME", 5))
NUM_SHORT_URLS: int = int(os.getenv("NUM_SHORT_URLS", 10))
NUM_WORKERS: int = int(os.getenv("NUM_WORKERS", 10))

if GENERATE_SHORT_URL_LENGTH > SHORTCODE_MAX:
    raise RuntimeError(
        f"GENERATE_SHORT_URL_LENGTH ({GENERATE_SHORT_URL_LENGTH}) cannot be greater than ({SHORTCODE_MAX})"
    )
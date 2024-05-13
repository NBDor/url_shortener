import logging
from re import S
import string
import time
import random
from zoneinfo import available_timezones
from django.db import transaction
from .models import AvailableShortURL, ShortURL
from .settings import GENERATE_SHORT_URL_LENGTH, MAX_EXECUTION_TIME
from .locks import short_url_lock

from typing import Optional


def generate_random_key(length: int) -> str:
    chars: str = string.ascii_letters + string.digits
    short_url: str = ''.join(random.choice(chars) for _ in range(length))
    return short_url


def create_unique_short_url(length: int = GENERATE_SHORT_URL_LENGTH) -> Optional[str]:
    start_time = time.time()
    while True:
        if time.time() - start_time > MAX_EXECUTION_TIME:
            logging.error("Timeout reached - Could not generate a unique short URL: increasing length by 1")
            return None
        new_url: str = generate_random_key(length)
        with short_url_lock:
            short_url_exists = ShortURL.objects.filter(short_url=new_url).exists()
            available_short_url_exists = AvailableShortURL.objects.filter(short_url=new_url).exists()
            if not short_url_exists and not available_short_url_exists:
                return new_url
        

def get_available_short_url() -> Optional[str]:
    with transaction.atomic():
        try:
            item = AvailableShortURL.objects.earliest('timestamp')
            short_url = item.short_url
            item.delete()
            return short_url
        except AvailableShortURL.DoesNotExist:
            return None
        

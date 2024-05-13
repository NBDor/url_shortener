import logging
import threading
from django.db import transaction
from .settings import NUM_SHORT_URLS, NUM_WORKERS, GENERATE_SHORT_URL_LENGTH
from .locks import short_url_lock
from typing import List

workers: List[threading.Thread] = []
shutdown_event = threading.Event()


def worker() -> None:
    # Import inside the function to avoid issue with Django not being ready
    from .models import AvailableShortURL
    
    while not shutdown_event.is_set():
        try:
            # Check if the number of available short URLs is below the threshold
            if AvailableShortURL.objects.count() < NUM_SHORT_URLS * 10:
                generate_and_save_short_url()
        except Exception as e:
            logging.error(e, exc_info=True)


def generate_and_save_short_url() -> None:
    # Import inside the function to avoid issue with Django not being ready
    from .utils import create_unique_short_url
    from .models import AppConfig, ShortURL

    with transaction.atomic():
        # Get or create the configuration for the short URL length
        config, _ = AppConfig.objects.get_or_create(
            key='generate_short_url_length',
            defaults={'value': str(GENERATE_SHORT_URL_LENGTH)}
        )
        url_length = int(config.value)

        # Calculate the maximum number of combinations for the current URL length
        max_combinations = 62 ** url_length

        # Get the current number of short URLs in the database
        num_short_urls = ShortURL.objects.count()

        # Generate a unique short URL
        available_url: str = create_unique_short_url(length=url_length)

        # If no available URL is found or the maximum combinations are reached,
        # increase the URL length and generate a new unique short URL
        if not available_url or num_short_urls >= max_combinations:
            url_length = increase_url_length(config)
            available_url: str = create_unique_short_url(length=url_length)

        # Acquire the lock to ensure thread safety when creating the short URL
        with short_url_lock:
            save_available_short_url(available_url)

def increase_url_length(config) -> int:
    with transaction.atomic():
        url_length = int(config.value) + 1
        config.value = str(url_length)
        config.save()
    return url_length

def save_available_short_url(available_url: str) -> None:
    from .models import AvailableShortURL
    with transaction.atomic():
        AvailableShortURL.objects.create(short_url=available_url)


def start_worker_threads() -> None:
    global workers  # Declare that we're using the global variable
    workers = []
    for _ in range(NUM_WORKERS):
        t: threading.Thread = threading.Thread(target=worker)
        workers.append(t)
        t.start()

def graceful_shutdown():
    global workers  # Declare that we're using the global variable
    shutdown_event.set()  # Signal worker threads to stop
    logging.info(f"Waiting for {len(workers)} worker threads to finish...")
    for t in workers:
        logging.info(f"Waiting for worker thread {t} to finish...")
        t.join()  # Wait for worker threads to finish
    # Close shared resources
    close_shared_resources()


def close_shared_resources():
    try:
        # Close shared database connection
        from django.db import connections
        for conn in connections.all():
            conn.close()
    except Exception as e:
        logging.error(f"Error closing shared resources: {e}")

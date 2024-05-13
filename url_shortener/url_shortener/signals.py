import signal
from shortener.queue_manager import graceful_shutdown

def handle_shutdown(sig, frame):
    print('Received signal to terminate, initiating graceful shutdown...')
    graceful_shutdown()
    quit()


def register_signal_handlers():
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

import threading
import time
from GroundStation import Ground
from ftpdownload import download_files_ftp

# Create an Event object
stop_event = threading.Event()


def ftp_task():
    while not stop_event.is_set():
        download_files_ftp('bifrost0602.duckdns.org', 'bifrost', '1234', 2025, '/home/bifrost/Documents',
                           'C:/Users/henry/Desktop/cansat/images/jpg', 'C:/Users/henry/Desktop/cansat/images/txt', 'downloaded_files.json')
        time.sleep(1)


def ground_task():
    try:
        Ground()
    finally:
        # If the ground task finishes, signal the other thread to stop
        stop_event.set()


thread1 = threading.Thread(target=ftp_task)
thread2 = threading.Thread(target=ground_task)

thread1.start()
thread2.start()

thread1.join()
thread2.join()

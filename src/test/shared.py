import queue
import threading
from config_loader import load_config

# shared frame queue
config = load_config("../config/config.json")
QUEUE_MAXSIZE = config["queue_maxsize"]

frame_queue = queue.Queue(maxsize=QUEUE_MAXSIZE)  
result_queue = queue.Queue(maxsize=30)
stop_event = threading.Event()
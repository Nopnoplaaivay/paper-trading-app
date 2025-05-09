import queue
import threading

EXECUTION_QUEUE = queue.Queue()
MESSAGE_QUEUE = queue.Queue()
STOP_EVENT = threading.Event()
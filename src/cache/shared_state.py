import queue
import threading

MESSAGE_QUEUE = queue.Queue()

STOP_EVENT = threading.Event()
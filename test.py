import threading
import queue
import paho.mqtt.client as mqtt
import redis
import json
import time
import logging
import os
import signal # Để xử lý dừng chương trình

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')

# --- Cấu hình ---
MQTT_BROKER = "your_mqtt_broker_address"
MQTT_PORT = 1883
MQTT_TOPICS = [
    ("stock/price/+", 0),   # Dấu + là wildcard cho 1 level
    ("stock/index/+", 0),
    ("stock/match/+", 0),
    ("stock/session", 0)
]
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
NUM_REDIS_WORKERS = 3 # Số lượng thread xử lý ghi vào Redis

# --- Hàng đợi và Event dừng ---
message_queue = queue.Queue()
stop_event = threading.Event() # Dùng để báo hiệu dừng cho các worker

# --- Kết nối Redis (nên dùng ConnectionPool) ---
# Pool an toàn cho việc chia sẻ giữa các thread
redis_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

# --- Hàm xử lý của Worker ---
def redis_worker(worker_id, redis_connection):
    """Thread xử lý tin nhắn từ queue và ghi vào Redis"""
    logging.info(f"Worker {worker_id} bắt đầu.")
    while not stop_event.is_set():
        try:
            # Lấy task từ queue, chờ tối đa 1 giây nếu rỗng
            # Timeout giúp worker kiểm tra stop_event định kỳ
            topic, payload_str = message_queue.get(block=True, timeout=1)

            try:
                # 1. Parse Payload (ví dụ là JSON)
                data = json.loads(payload_str)
                logging.debug(f"Worker {worker_id} nhận: Topic={topic}, Data={data}")

                # 2. Xử lý dựa trên Topic và ghi vào Redis
                topic_parts = topic.split('/')
                if topic.startswith("stock/price/"):
                    symbol = topic_parts[-1]
                    # Ví dụ: Lưu giá vào Hash, key là 'price:<symbol>'
                    redis_key = f"price:{symbol}"
                    # Dùng HMSET hoặc HSET (nếu data là dict)
                    redis_connection.hset(redis_key, mapping=data)
                    logging.info(f"Worker {worker_id}: Updated price for {symbol}")

                elif topic.startswith("stock/index/"):
                    index_name = topic_parts[-1]
                    redis_key = f"index:{index_name}"
                    # Giả sử data chứa các trường 'value', 'change', 'pct_change'
                    redis_connection.hset(redis_key, mapping=data)
                    logging.info(f"Worker {worker_id}: Updated index {index_name}")

                elif topic.startswith("stock/match/"):
                    symbol = topic_parts[-1]
                    redis_key = f"match:{symbol}"
                    # Ví dụ: Lưu các lệnh khớp vào List (dùng LPUSH, giới hạn độ dài bằng LTRIM)
                    redis_connection.lpush(redis_key, json.dumps(data)) # Lưu lại dạng JSON string
                    redis_connection.ltrim(redis_key, 0, 999) # Giữ lại 1000 lệnh khớp mới nhất
                    logging.info(f"Worker {worker_id}: Added match for {symbol}")

                elif topic == "stock/session":
                    redis_key = "stock:session"
                    # Ví dụ: Lưu trạng thái phiên (OPEN, CLOSE, ATO...) vào String
                    redis_connection.set(redis_key, data.get("status", "UNKNOWN"))
                    logging.info(f"Worker {worker_id}: Updated session status")

                else:
                    logging.warning(f"Worker {worker_id}: Không xử lý topic {topic}")

            except json.JSONDecodeError:
                logging.error(f"Worker {worker_id}: Lỗi parse JSON từ topic {topic}: {payload_str[:100]}...")
            except redis.RedisError as e:
                logging.error(f"Worker {worker_id}: Lỗi Redis khi xử lý topic {topic}: {e}")
            except Exception as e:
                logging.error(f"Worker {worker_id}: Lỗi không xác định khi xử lý topic {topic}: {e}", exc_info=True)
            finally:
                # Rất quan trọng: Báo là đã xử lý xong task này
                message_queue.task_done()

        except queue.Empty:
            # Hàng đợi rỗng, tiếp tục vòng lặp để kiểm tra stop_event
            continue
        except Exception as e:
            # Lỗi không mong muốn trong vòng lặp chính của worker
            logging.error(f"Worker {worker_id}: Lỗi nghiêm trọng: {e}", exc_info=True)
            # Có thể cân nhắc dừng worker hoặc khởi động lại

    logging.info(f"Worker {worker_id} dừng.")


# --- Callbacks cho MQTT ---
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Kết nối MQTT thành công!")
        # Subscribe lại khi kết nối lại
        client.subscribe(MQTT_TOPICS)
        logging.info(f"Đã subcribe tới các topic: {[t[0] for t in MQTT_TOPICS]}")
    else:
        logging.error(f"Kết nối MQTT thất bại, mã lỗi: {rc}")

def on_message(client, userdata, msg):
    """Callback khi nhận tin nhắn MQTT - NHANH GỌN"""
    try:
        # Chỉ đưa vào queue, không xử lý nặng ở đây
        message_queue.put((msg.topic, msg.payload.decode('utf-8')))
        logging.debug(f"Received message on topic '{msg.topic}'. Added to queue.")
    except Exception as e:
        logging.error(f"Lỗi trong on_message khi đưa vào queue: {e}", exc_info=True)

def on_disconnect(client, userdata, rc):
     logging.warning(f"Mất kết nối MQTT, mã lỗi: {rc}. Đang thử kết nối lại...")
     # Thư viện paho-mqtt thường tự động thử kết nối lại

# --- Hàm xử lý tín hiệu dừng ---
def signal_handler(sig, frame):
    logging.info("Nhận tín hiệu dừng (Ctrl+C)...")
    stop_event.set() # Báo cho các worker dừng
    # Có thể thêm các bước dọn dẹp khác ở đây
    # Ví dụ: Đóng kết nối MQTT client.disconnect() nếu dùng loop_start()

# --- Main ---
if __name__ == "__main__":
    # Đăng ký xử lý tín hiệu Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 1. Khởi tạo MQTT Client
    mqtt_client = mqtt.Client(client_id=f"redis_cacher_{os.getpid()}") # Client ID duy nhất
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.on_disconnect = on_disconnect

    try:
        logging.info(f"Đang kết nối tới MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        logging.error(f"Không thể kết nối tới MQTT Broker: {e}")
        exit(1)

    # 2. Khởi tạo và chạy các Worker Thread
    worker_threads = []
    for i in range(NUM_REDIS_WORKERS):
        # Mỗi worker lấy connection riêng từ pool
        redis_conn = redis.Redis(connection_pool=redis_pool)
        thread_name = f"RedisWorker-{i+1}"
        worker = threading.Thread(target=redis_worker, args=(i+1, redis_conn), name=thread_name)
        worker.start()
        worker_threads.append(worker)
    logging.info(f"Đã khởi chạy {NUM_REDIS_WORKERS} Redis worker thread.")

    # 3. Bắt đầu MQTT Loop (blocking)
    # loop_forever() sẽ chạy cho đến khi client.disconnect() được gọi hoặc có lỗi
    # Nó cũng tự xử lý việc kết nối lại.
    logging.info("Bắt đầu vòng lặp MQTT...")
    mqtt_client.loop_forever() # Đây là lệnh blocking

    # --- Code phía sau loop_forever() chỉ chạy khi loop dừng ---
    logging.info("Vòng lặp MQTT đã dừng.")

    # 4. Dừng các Worker (nếu loop_forever bị ngắt bởi disconnect hoặc lỗi)
    if not stop_event.is_set():
         logging.info("Gửi tín hiệu dừng đến các worker...")
         stop_event.set() # Đảm bảo các worker biết cần dừng

    logging.info("Đang chờ các worker hoàn thành công việc còn lại...")
    # Không cần chờ queue join nếu không quan trọng việc xử lý hết queue khi dừng đột ngột
    # message_queue.join() # Chờ queue rỗng và tất cả task_done được gọi

    for worker in worker_threads:
        worker.join() # Chờ từng thread worker kết thúc

    logging.info("Tất cả worker đã dừng. Chương trình kết thúc.")
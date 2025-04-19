import os
import redis

from src.utils.logger import LOGGER


class RedisConnectionPool:
    def __init__(self, host, port, db, decode_responses):
        self.pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            decode_responses=decode_responses
        )

    def get_connection(self):
        """Lấy một kết nối Redis từ pool."""
        try:
            conn = redis.Redis(connection_pool=self.pool)
            conn.ping()
            return conn
        except redis.ConnectionError as e:
            LOGGER.error(f"Failed to connect to Redis server: {e}")
            return None


REDIS_POOL = RedisConnectionPool(host=os.getenv("REDIS_HOST"), port=6379, db=0, decode_responses=True)


#
# def redis_worker_loop(worker_id):
#     """Vòng lặp chính của worker thread để xử lý tin nhắn từ queue."""
#     logging.info(f"Worker {worker_id} bắt đầu.")
#     redis_connection = get_redis_connection()
#
#     if not redis_connection:
#         logging.error(f"Worker {worker_id} không thể lấy kết nối Redis. Đang dừng.")
#         return # Dừng worker nếu không có kết nối Redis
#
#     while not stop_event.is_set():
#         try:
#             topic, payload_str = message_queue.get(block=True, timeout=1)
#
#             # Gọi hàm xử lý riêng biệt
#             process_message(worker_id, topic, payload_str, redis_connection)
#
#             message_queue.task_done()
#
#         except queue.Empty:
#             # Queue rỗng, tiếp tục vòng lặp để kiểm tra stop_event
#             continue
#         except redis.ConnectionError as e:
#              logging.error(f"Worker {worker_id}: Mất kết nối Redis: {e}. Đang thử lấy lại kết nối...")
#              # Đóng kết nối cũ (nếu có)
#              if redis_connection:
#                  try:
#                       redis_connection.close() # Đóng kết nối hiện tại
#                  except: pass # Bỏ qua lỗi nếu đóng không thành công
#
#              # Cố gắng lấy kết nối mới
#              redis_connection = get_redis_connection()
#              if not redis_connection:
#                   logging.error(f"Worker {worker_id}: Không thể kết nối lại Redis. Tạm dừng 5s.")
#                   # Chờ một chút trước khi thử lại hoặc có thể dừng hẳn worker
#                   stop_event.wait(5) # Chờ 5s hoặc đến khi stop_event được set
#              else:
#                   logging.info(f"Worker {worker_id}: Đã kết nối lại Redis.")
#              # Bỏ qua message hiện tại hoặc đưa lại vào queue? (Tuỳ chiến lược)
#
#         except Exception as e:
#             logging.error(f"Worker {worker_id}: Lỗi nghiêm trọng trong vòng lặp: {e}", exc_info=True)
#             # Có thể dừng worker hoặc tạm dừng rồi thử lại
#
#     # Dọn dẹp khi worker dừng
#     if redis_connection:
#         try:
#             redis_connection.close()
#             logging.info(f"Worker {worker_id}: Đã đóng kết nối Redis.")
#         except Exception as e:
#             logging.error(f"Worker {worker_id}: Lỗi khi đóng kết nối Redis: {e}")
#
#     logging.info(f"Worker {worker_id} đã dừng.")
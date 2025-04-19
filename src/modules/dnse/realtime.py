import threading
import signal
import time
import os

from src.cache.config import DNSEConfigs
from src.cache.worker import RedisWorker
from src.cache.shared_state import STOP_EVENT, MESSAGE_QUEUE
from src.modules.dnse.mqtt.mqtt import DNSEMqtt
from src.utils.logger import LOGGER


# --- Lớp điều phối chính ---
class DNSERealtimeCacher:
    def __init__(self):
        self.worker_threads = []
        LOGGER.info("RealtimeCacher instance initialized.")
        if not os.getenv("DNSE_USERNAME") or not os.getenv("DNSE_PASSWORD"):
            raise Exception("Missing required environment variables: DNSE_USERNAME or DNSE_PASSWORD.")

    def start_redis_workers(self):
        """Khởi tạo và chạy các Redis worker thread."""
        if not self.worker_threads: # Chỉ khởi tạo nếu danh sách rỗng
            num_workers = getattr(DNSEConfigs, 'NUM_REDIS_WORKERS', 1)
            LOGGER.info(f"Starting {num_workers} Redis worker threads...")
            for i in range(num_workers):
                thread_name = f"RedisWorker-{i+1}"
                worker = threading.Thread(target=RedisWorker.loop, args=(i+1,), name=thread_name)
                # worker.daemon = False # Mặc định là False, đảm bảo chờ chúng kết thúc
                worker.start()
                self.worker_threads.append(worker)
            LOGGER.info(f"Successfully launched {len(self.worker_threads)} Redis worker threads.")
            return True
        else:
            LOGGER.warning("Redis worker threads seem to be already running.")
            return True

    def signal_handler(self, sig, frame):
        """Xử lý tín hiệu dừng (SIGINT, SIGTERM) một cách an toàn."""
        LOGGER.info(f"Received signal {signal.Signals(sig).name}. Initiating shutdown...")

        # 1. Báo cho các worker dừng (nếu chưa)
        if not STOP_EVENT.is_set():
            LOGGER.info("Setting STOP_EVENT for workers...")
            STOP_EVENT.set()

        # 2. Ngắt kết nối MQTT client (nếu đang kết nối)
        try:
            if DNSEMqtt.client and DNSEMqtt.client.is_connected():
                LOGGER.info("Disconnecting MQTT client...")
                DNSEMqtt.client.disconnect() # Sẽ làm loop_forever() kết thúc
                DNSEMqtt.client.loop_stop() # Thêm loop_stop nếu cần thiết để dừng hẳn luồng mạng của Paho
            elif DNSEMqtt.client:
                LOGGER.info("MQTT client was not connected.")
            else:
                LOGGER.info("MQTT client was not initialized.")
        except Exception as e:
             LOGGER.error(f"Error during MQTT client disconnect: {e}", exc_info=True)

    def shutdown_workers(self):
        """Chờ các worker thread hoàn thành và ghi log."""
        LOGGER.info("Waiting for Redis worker threads to complete...")
        start_time = time.time()
        shutdown_timeout = 10.0 # Tổng thời gian chờ tất cả worker

        # Gửi join tới tất cả trước
        for worker in self.worker_threads:
             if worker.is_alive():
                 worker.join(timeout=0.1) # Join ngắn để kiểm tra nhanh

        # Chờ đợi với timeout tổng
        while any(w.is_alive() for w in self.worker_threads) and time.time() - start_time < shutdown_timeout:
             time.sleep(0.5)

        # Kiểm tra lại và log kết quả
        remaining_workers = []
        for worker in self.worker_threads:
            if worker.is_alive():
                LOGGER.warning(f"Worker {worker.name} did not stop within the timeout.")
                remaining_workers.append(worker.name)
            else:
                LOGGER.info(f"Worker {worker.name} stopped successfully.")

        if not remaining_workers:
            LOGGER.info("All Redis worker threads have stopped.")
        else:
            LOGGER.warning(f"Workers still running: {', '.join(remaining_workers)}")

        # Log trạng thái queue cuối cùng
        try:
             qsize = MESSAGE_QUEUE.qsize()
             if qsize > 0:
                 LOGGER.warning(f"There are still {qsize} messages left in the queue.")
             else:
                 LOGGER.info("Message queue is empty.")
        except NotImplementedError:
              # queue.qsize() có thể không đáng tin cậy trên một số hệ thống
              LOGGER.info("Could not reliably determine the final queue size.")


    def run(self):
        """Hàm chính để khởi chạy và điều phối ứng dụng."""
        LOGGER.info("--- Starting Realtime Cacher Application ---")

        try:
            # 1. Đăng ký xử lý tín hiệu dừng (liên kết với phương thức của instance)
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            LOGGER.info("Signal handlers registered.")

            # 2. Khởi tạo và chạy các Worker Thread Redis
            if not self.start_redis_workers():
                # Sử dụng RuntimeError cho các lỗi nghiêm trọng khi khởi tạo
                raise RuntimeError("Failed to initialize Redis workers. Exiting.")

            # 3. Bắt đầu MQTT Service (blocking)
            LOGGER.info("Launching DNSEMqtt Service (this will block)...")
            # DNSEMqtt.run() xử lý vòng đời MQTT, bao gồm cả loop_forever()
            # Nó sẽ block ở đây cho đến khi bị ngắt bởi disconnect() hoặc lỗi
            DNSEMqtt.run()

        except KeyboardInterrupt:
            LOGGER.info("KeyboardInterrupt caught in main run loop. Shutdown should be in progress.")
            # Signal handler đã được gọi, chỉ cần đảm bảo STOP_EVENT được set
            if not STOP_EVENT.is_set():
                 LOGGER.warning("KeyboardInterrupt but STOP_EVENT was not set. Setting now.")
                 STOP_EVENT.set()

        except RuntimeError as e:
             LOGGER.error(f"Runtime error during startup: {e}")
             # Đảm bảo dừng nếu có lỗi
             if not STOP_EVENT.is_set(): STOP_EVENT.set()

        except Exception as e:
            LOGGER.error(f"An unexpected critical error occurred in the main loop: {e}", exc_info=True)
            # Đảm bảo dừng các worker nếu có lỗi nghiêm trọng
            if not STOP_EVENT.is_set():
                LOGGER.info("Setting STOP_EVENT due to critical error.")
                STOP_EVENT.set()
        finally:
            # --- Luôn thực hiện dọn dẹp ---
            LOGGER.info("MQTT service loop has ended. Proceeding with final shutdown...")

            # 4. Chờ các Worker hoàn thành (gọi phương thức dọn dẹp riêng)
            self.shutdown_workers()

            LOGGER.info("--- Realtime Cacher Application Finished ---")
            # sys.exit(0) # Thoát chương trình. Có thể bỏ nếu muốn trả về từ hàm run
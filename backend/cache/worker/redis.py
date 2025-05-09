import json
import redis
import queue

from backend.cache.shared_state import MESSAGE_QUEUE, STOP_EVENT
from backend.cache.connector import REDIS_POOL
from backend.cache.config import DNSEConfigs
from backend.utils.logger import LOGGER

class RedisWorker:
    @classmethod
    def loop(cls, worker_id):
        """Vòng lặp chính của worker thread để xử lý tin nhắn từ queue."""
        LOGGER.info(f"Worker {worker_id} start running...")
        redis_conn = REDIS_POOL.get_conn()

        if not redis_conn:
            LOGGER.error(f"Worker {worker_id} failed to connect to Redis. Stopping worker.")
            return

        while not STOP_EVENT.is_set():
            try:
                topic, payload_str = MESSAGE_QUEUE.get(block=True, timeout=1)
                cls.process_message(worker_id, topic, payload_str, redis_conn)

                MESSAGE_QUEUE.task_done()

            except queue.Empty:
                continue
            except redis.ConnectionError as e:
                LOGGER.error(f"Worker {worker_id}: Lost Redis Connection: {e}. Reconnecting...")
                if redis_conn:
                    try:
                        redis_conn.close()
                    except:
                        pass

                # Cố gắng lấy kết nối mới
                redis_conn = REDIS_POOL.get_conn()
                if not redis_conn:
                    LOGGER.error(f"Worker {worker_id}: failed to reconnect Redis. Waiting 5s.")
                    STOP_EVENT.wait(5)
                else:
                    LOGGER.info(f"Worker {worker_id}: Reconnected to Redis successfully.")

            except Exception as e:
                LOGGER.error(f"Worker {worker_id}: Loop Error {e}", exc_info=True)

        if redis_conn:
            try:
                redis_conn.close()
                LOGGER.info(f"Worker {worker_id}: closed connection to Redis.")
            except Exception as e:
                LOGGER.error(f"Worker {worker_id}: error closing connection to Redis: {e}")

        LOGGER.info(f"Worker {worker_id} stopped.")

    @classmethod
    def process_message(cls, worker_id, topic, payload, redis_conn):
        try:
            data = json.loads(payload)
            LOGGER.debug(f"Worker {worker_id} received: Topic={topic}, Data={data}")

            # Sử dụng hằng số từ config để kiểm tra topic
            if topic.startswith(DNSEConfigs.TOPIC_STOCK_INFO):
                symbol = data.get("symbol")
                if symbol:
                    redis_key = f"{DNSEConfigs.KEY_STOCK_INFO}:{symbol}"
                    redis_conn.hset(redis_key, mapping=data)
            elif topic.startswith(DNSEConfigs.TOPIC_OHLC_1M):
                symbol = data.get("symbol")
                if symbol:
                    redis_key = f"{DNSEConfigs.KEY_OHLC}:{symbol}"
                    redis_conn.hset(redis_key, mapping=data)
            elif topic.startswith(DNSEConfigs.TOPIC_TICK):
                symbol = data.get("symbol")
                if symbol:
                    redis_key = f"{DNSEConfigs.KEY_TICK}:{symbol}"
                    redis_conn.hset(redis_key, mapping=data)
            elif topic.startswith(DNSEConfigs.TOPIC_MARKET):
                market = data.get("indexName")
                if market:
                    redis_key = f"{DNSEConfigs.KEY_MARKET}:{market}"
                    redis_conn.hset(redis_key, mapping=data)
            else:
                LOGGER.warning(f"Worker {worker_id}: Error handling topic {topic}")

        except json.JSONDecodeError:
            LOGGER.error(f"Worker {worker_id}: Error parse JSON from topic {topic}: {payload[:100]}...")
        except redis.RedisError as e:
            LOGGER.error(f"Worker {worker_id}: Error Redis handling topic {topic}: {e}")
        except Exception as e:
            LOGGER.error(f"Worker {worker_id}: Error unexpected {topic}: {e}", exc_info=True)

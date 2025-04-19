from src.cache.connector import REDIS_POOL
from src.modules.dnse.realtime import DNSERealtimeCacher

if __name__ == "__main__":
    # redis_connection = REDIS_POOL.get_connection()
    # redis_connection.set("test_key", "test_value")

    dnse_cacher = DNSERealtimeCacher()
    dnse_cacher.run()
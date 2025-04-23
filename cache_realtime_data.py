from src.modules.dnse.realtime_cache.realtime import DNSERealtimeCacher

if __name__ == "__main__":
    # redis_conn = REDIS_POOL.get_conn()
    # redis_conn.set("test_key", "test_value")

    dnse_cacher = DNSERealtimeCacher()
    dnse_cacher.run()
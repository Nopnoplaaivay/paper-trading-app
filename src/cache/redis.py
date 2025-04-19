import os
import redis


# REDIS_HOST=192.168.1.6

RedisClient = redis.Redis(host=os.getenv("REDIS_HOST"), port=6379, db=0, decode_responses=True)

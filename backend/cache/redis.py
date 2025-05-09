import os
import redis

RedisClient = redis.Redis(host=os.getenv("REDIS_HOST"), port=6379, db=0, decode_responses=True)

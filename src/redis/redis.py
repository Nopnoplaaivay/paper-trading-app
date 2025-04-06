import redis
import json

from typing import Dict


RedisClient = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

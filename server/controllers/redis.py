# TODO: move to helpers
import redis

from server.constants import REDIS_HOST

r = redis.Redis(host=REDIS_HOST, port=6379, db=0)

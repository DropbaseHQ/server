import redis

from server.constants import DOCKER_ENV

REDIS_HOST = "host.docker.internal" if DOCKER_ENV else "localhost"

r = redis.Redis(host=REDIS_HOST, port=6379, db=0)

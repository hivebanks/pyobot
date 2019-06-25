import redis

POOL = redis.ConnectionPool(host='', port=6379, password='', max_connections=1000)
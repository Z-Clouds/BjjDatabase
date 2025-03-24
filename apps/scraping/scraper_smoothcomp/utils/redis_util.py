import redis
import json

# Redis connection (defaults to localhost:6379)
redis_conn = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

BRACKET_QUEUE_KEY = "bracket_queue"
MATCH_QUEUE_KEY = "match_queue"
FAILED_MATCHES_KEY = "match_failed"
FAILED_BRACKETS_KEY = "bracket_failed"

# ========== BRACKETS ==========

def enqueue_bracket(payload):
    redis_conn.lpush(BRACKET_QUEUE_KEY, json.dumps(payload))

def dequeue_bracket():
    item = redis_conn.rpop(BRACKET_QUEUE_KEY)
    return json.loads(item) if item else None

def requeue_bracket(payload):
    redis_conn.rpush(BRACKET_QUEUE_KEY, json.dumps(payload))

def log_failed_bracket(payload):
    redis_conn.sadd(FAILED_BRACKETS_KEY, json.dumps(payload))

def get_bracket_queue_size():
    return redis_conn.llen(BRACKET_QUEUE_KEY)

def get_failed_brackets_count():
    return redis_conn.scard(FAILED_BRACKETS_KEY)

# ========== MATCHES ==========

def enqueue_match(payload):
    redis_conn.lpush(MATCH_QUEUE_KEY, json.dumps(payload))

def dequeue_match():
    item = redis_conn.rpop(MATCH_QUEUE_KEY)
    return json.loads(item) if item else None

def requeue_match(payload):
    redis_conn.rpush(MATCH_QUEUE_KEY, json.dumps(payload))

def log_failed_match(payload):
    redis_conn.sadd(FAILED_MATCHES_KEY, json.dumps(payload))

def get_match_queue_size():
    return redis_conn.llen(MATCH_QUEUE_KEY)

def get_failed_matches_count():
    return redis_conn.scard(FAILED_MATCHES_KEY)

# ========== UTILITIES ==========

def flush_queues():
    redis_conn.delete(BRACKET_QUEUE_KEY)
    redis_conn.delete(MATCH_QUEUE_KEY)
    redis_conn.delete(FAILED_MATCHES_KEY)
    redis_conn.delete(FAILED_BRACKETS_KEY)


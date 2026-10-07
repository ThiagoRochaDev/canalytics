import base64
import hashlib
import hmac
import secrets
import time
from collections import defaultdict, deque

from fastapi import HTTPException


def hash_password(password):
    salt = secrets.token_bytes(16)
    value = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1)
    return base64.b64encode(salt + value).decode()


def verify_password(password, encoded):
    raw = base64.b64decode(encoded)
    actual = hashlib.scrypt(password.encode(), salt=raw[:16], n=16384, r=8, p=1)
    return hmac.compare_digest(actual, raw[16:])


class RateLimit:
    def __init__(self):
        self.buckets = defaultdict(deque)

    def check(self, key, limit=10, seconds=300):
        now = time.monotonic()
        # Bound memory, including unauthenticated traffic.
        if len(self.buckets) > 10000:
            self.buckets.clear()
        bucket = self.buckets[key]
        while bucket and bucket[0] < now - seconds:
            bucket.popleft()
        if len(bucket) >= limit:
            raise HTTPException(429, "Muitas tentativas. Aguarde alguns minutos.")
        bucket.append(now)

import hashlib
import hmac

from config import HASH_KEY


def get_user_hash(userid: int):
    res = hmac.new(HASH_KEY, str(userid).encode('utf-8'), digestmod=lambda: hashlib.blake2b(digest_size=5)).hexdigest()
    return res

def get_photo_hash(photo_name: str):
    return hmac.new(HASH_KEY, photo_name.encode('utf-8'), digestmod=lambda: hashlib.blake2b(digest_size=5)).hexdigest()


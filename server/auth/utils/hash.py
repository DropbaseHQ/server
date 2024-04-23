import hashlib


def get_confirmation_token_hash(payload: str):
    hash_object = hashlib.sha256(payload.encode("utf-8"))
    return hash_object.hexdigest()

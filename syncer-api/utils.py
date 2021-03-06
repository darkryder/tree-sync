from hashlib import md5
from custom_exceptions import CouldNotHashException
# from base import SyncTree


def hash_md5(obj):
    if any(map((lambda x: obj == x), [None, ''])): return '0'
    try:
        obj = str(obj)
    except:
        raise CouldNotHashException("Could not convert object to string")
    temp = md5()
    temp.update(obj)
    return temp.hexdigest()


def check_valid_hash(h):
    if not isinstance(h, str): return False
    return all((
        len(h) == 32,
        h.isalnum()))

def load_sync_api_into_memcache(tree):
    pass

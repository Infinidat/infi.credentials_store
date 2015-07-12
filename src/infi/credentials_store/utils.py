import random
import hashlib
from base64 import b64encode, b64decode


MAGIC_VER = 'ENC:1'


default_mask_key = hashlib.sha512('CrD').digest()


def get_default_mask_key():
    return default_mask_key


def set_default_mask_key(k):
    global default_mask_key
    default_mask_key = k


def set_hash_seed(seed):
    set_default_mask_key(hashlib.sha512(seed).digest())


def mask(s, k=None):
    k = k or get_default_mask_key()
    s += '\x00' * ((16 - len(s) % 16) % 16)
    s1 = random.randint(1, 255)
    return MAGIC_VER + b64encode(chr(s1) + ''.join([chr(ord(c) ^ (ord(k[i % len(k)]) ^ s1)) for i, c in enumerate(s)]))


def unmask(s, k=None):
    k = k or get_default_mask_key()
    if not s.startswith(MAGIC_VER):
        return s
    try:
        s = b64decode(s[len(MAGIC_VER):])
    except TypeError:
        return ''
    s1 = ord(s[0])
    return ''.join([chr(ord(c) ^ (ord(k[i % len(k)]) ^ s1)) for i, c in enumerate(s[1:])]).rstrip('\x00')


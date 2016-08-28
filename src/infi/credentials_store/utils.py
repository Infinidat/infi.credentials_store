import sys
import random
import hashlib
from base64 import b64encode, b64decode


PY3 = sys.version_info[0] == 3
MAGIC_VER = 'ENC:1'


default_mask_key = hashlib.sha512(b'CrD').digest()


def _ord(c):
    # single char (byte/str) to int
    if isinstance(c, int):
        return c
    return ord(c)

def _chr(o):
    # int to byte (if available) or str
    if PY3:
        return bytes([o])
    return chr(o)


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
    xored_s = b''.join([_chr(_ord(c) ^ (_ord(k[i % len(k)]) ^ s1)) for i, c in enumerate(s)])
    return MAGIC_VER + b64encode(_chr(s1) + xored_s).decode("ascii")


def unmask(s, k=None):
    k = k or get_default_mask_key()
    if not s.startswith(MAGIC_VER):
        return s
    try:
        s = b64decode(s[len(MAGIC_VER):])
    except TypeError:
        return ''
    s1 = _ord(s[0])
    return ''.join([chr(_ord(c) ^ (_ord(k[i % len(k)]) ^ s1)) for i, c in enumerate(s[1:])]).rstrip('\x00')

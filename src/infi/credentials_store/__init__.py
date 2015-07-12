__import__("pkg_resources").declare_namespace(__name__)

from .base import BaseCredentialsStore, FileCredentialsStore
from .base import NoCredentialsException, Credentials
from .base import DEFAULT
from .cli import CLICredentialsStore
from .utils import set_hash_seed, get_default_mask_key, set_default_mask_key

import json
import os
import platform
from .utils import mask, unmask


class NoCredentialsException(Exception):
    pass


class Credentials(object):
    """
    An object for storing a username + password pair.
    """

    def __init__(self, username, password):
        self._username = username
        self._password = password

    def get_username(self):
        return self._username

    def get_password(self):
        return self._password

    @classmethod
    def from_dict(cls, data):
        return cls(data['username'], data['password'] if data.get('clear_text', True) else unmask(data['password']))

    def to_dict(self):
        return dict(username=self.get_username(), password=mask(self.get_password()), clear_text=False,)

    @classmethod
    def from_json(cls, data):
        d = json.loads(data)
        return cls(d['username'], d['password'] if d.get('clear_text', True) else unmask(d['password']))

    def to_json(self):
        return json.dumps(dict(username=self.get_username(), password=mask(self.get_password()), clear_text=False))


DEFAULT = '*'


class BaseCredentialsStore(object):
    """
    An abstract base class for storing credentials on behalf of the user.
    Each system is identifed by a key, which could be its serial or host address.
    There are two levels of credentials: default and per key.
    The default credentials are used if there are no specific credentials for the given system.
    """

    def __init__(self):
        self.temp_credentials = {}

    def get_credentials(self, key):
        """
        Get existing credentials for the given system, or ask the user for credentials.
        Returns a Credentials object.
        Note: user-provided credentials are not saved for future use. Call set_credentials if you need to save them.
        """
        raise NotImplementedError()

    def get_existing_credentials(self, key):
        """
        Get existing credentials for the given system, after ensuring that they are valid.
        Returns a Credentials object or None.
        """
        raise NotImplementedError()

    def set_credentials(self, key, credentials):
        """
        Set the credentials for a specific system.
        """
        raise NotImplementedError()

    def set_default_credentials(self, credentials):
        """
        Set the default credentials.
        """
        raise NotImplementedError()

    def get_default_credentials(self):
        """
        Get the default credentials.
        """
        raise NotImplementedError()

    def authenticate(self, key, credentials):
        """
        Returns the user's role if the credentials are valid for the given system, or None if not.
        """
        raise NotImplementedError()

    def get_temp_credentials_dict(self):
        return {key: Credentials.to_dict(value) for key, value in self.temp_credentials.items() if value}

    def replace_temp_credentials_dict(self, temp_credentials_dict):
        self.temp_credentials = {key: Credentials.from_dict(value)
                                 for key, value in temp_credentials_dict.items() if value}


class FileCredentialsStore(BaseCredentialsStore):
    """
    A credentials store that uses a file as its backend
    """

    def __init__(self, file_basename):
        super(FileCredentialsStore, self).__init__()
        self._file_basename = file_basename
        self._filepath = None

    def get_file_path(self):
        if self._filepath is None:
            self._filepath = self._build_file_path()
        return self._filepath

    def _get_file_folder(self):
        return NotImplementedError()

    def _build_file_path(self):
        if platform.system() == 'Windows':
            root = os.environ.get("USERPROFILE", "C:\WINDOWS\Temp")
        else:
            fallback = os.path.expanduser('~')
            root = os.environ.get('XDG_DATA_HOME', None) or fallback
        return os.path.join(root, self._get_file_folder(), self._file_basename)

    def _ensure_file_exists(self, filepath):
        root = os.path.dirname(filepath)
        if not os.path.isdir(root):
            os.makedirs(root)
        if not os.path.isfile(filepath):
            with open(filepath, 'w'):
                pass
            os.chmod(filepath, 0o600)

    def _load_file_by_path(self, path):
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except ValueError:
            return {}

    def _handle_upgrade(self, data):
        # to meet the requirement to obfuscate remaining clear-text from previous versions,
        # we need to re-write the file even when the user did not change the credentials
        if data and any(value.get('clear_text', True) for value in data.values()):
            with open(self.get_file_path(), 'w') as f:
                json.dump({key: Credentials.from_dict(value).to_dict() for key, value in data.items()}, f, indent=4)

    def _load_file(self):
        data = self._load_file_by_path(self.get_file_path())
        self._handle_upgrade(data)
        return data

    def _load_credentials(self, key):
        data = self._load_file().get(str(key))
        return Credentials.from_dict(data) if data else None

    def get_existing_credentials(self, key):
        # Look for existing credentials, either for the given system or global
        for option in (str(key), DEFAULT):
            credentials = self._load_credentials(option)
            if self.authenticate(key, credentials):
                return credentials
        return None

    def set_credentials(self, key, credentials):
        self._ensure_file_exists(self.get_file_path())
        data = self._load_file()
        data[str(key)] = credentials.to_dict()
        with open(self.get_file_path(), 'w') as f:
            json.dump(data, f, indent=4)

    def set_default_credentials(self, credentials):
        self.set_credentials(DEFAULT, credentials)

    def get_default_credentials(self):
        return self._load_credentials(DEFAULT)

    def get_credentials_dict(self):
        return {key: Credentials.from_dict(value) for key, value in self._load_file().items() if value}

    def reset_credentials(self):
        if os.path.exists(self.get_file_path()):
            os.remove(self.get_file_path())

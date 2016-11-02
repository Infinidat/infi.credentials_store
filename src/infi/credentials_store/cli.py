from __future__ import print_function

import sys
from .base import FileCredentialsStore, Credentials

if sys.version_info > (3, 0):
    _input = input
else:
    _input = raw_input


class CLICredentialsStore(FileCredentialsStore):
    """
    A credentials store for CLI applications.
    - Prompts the user for username and password, and whether to save them for later use.
    - Keeps new credentials in memory unless asked to remember them
    """

    def _load_credentials(self, key):
        return self.temp_credentials.get(str(key)) or super(CLICredentialsStore, self)._load_credentials(key)

    def ask_for_username(self):
        username = None
        while not username:
            username = _input('Username: ').strip()
        return username

    def ask_for_password(self):
        from getpass import getpass
        password = None
        while not password:
            password = getpass('Password: ').strip()
        return password

    def ask_to_save_credentials(self):
        return _input('Remember username and password [y/N]? ').lower() in ('y', 'yes')

    def get_credentials(self, key):
        credentials = self.get_existing_credentials(key)
        if not credentials:
            credentials = self.ask_credentials(key)
        return credentials

    def ask_credentials_prompt(self, key):
        print('\nConnecting to ' + str(key))

    def ask_credentials(self, key):
        self.ask_credentials_prompt(key)
        while True:
            username = self.ask_for_username()
            password = self.ask_for_password()
            credentials = Credentials(username, password)
            if self.authenticate(key, credentials):
                self.temp_credentials[str(key)] = credentials
                if self.ask_to_save_credentials():
                    self.set_credentials(key, credentials)
                return credentials
            print('Invalid username or password')

    def set_credentials(self, key, credentials):
        self.temp_credentials[str(key)] = credentials
        super(CLICredentialsStore, self).set_credentials(key, credentials)

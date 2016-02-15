Overview
========
This project is used to prompt the user for a username and password for any type of system, and optionally
store the credentials on the local computer for future use.

Usage
-----

First, define a subclass. Subclasses need to define:

* `_get_file_folder` which is a name of a folder that will be created in the user's profile directory where the credentials will be stored.
* `authenticate`, which will be called to verify the credentials are valid (if they are not, the user will be prompted to reenter the credentials)
* `ask_credentials_prompt`, which prints a prompt before asking for the credentials.

For example:

    class MyCLICrdentialsStore(CLICredentialsStore):
        def _get_file_folder(self):
            return ".infi.credentials_store"

        def authenticate(self, key, credentilas):
            return True

        def ask_credentials_prompt(self, key):
            print '\nConnecting to the cool system ' + str(key)

Next, to initiate the store pass the name of a file to be created inside the directory of the credentials store.
Then, to use the store, pass a key for a specific system for which credentials are needed.

    store = MyCLICrdentialsStore("cool_systems")
    credentials = store.get_credentials("cool system 1")

`get_credentials` will look for existing credentials in its file, or prompt the user to input its username and password.
Storing the credentials in the file is optional, and is controlled by the user.

`credentials` object are used by calling `get_username` and `get_password`

    connect_to_cool_system(credentials.get_username(), credentials.get_password()


Checking out the code
=====================
To run this code from the repository for development purposes, run the following:

    easy_install -U infi.projector
    projector devenv build


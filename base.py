import os

from configparser import ConfigParser


DEFAULT_CONFIG_STRING = """
[MODS]
directory = ./storage

[PACKS]
directory = ./packs
use symlinks = True
"""

config = ConfigParser()
config.read_string(DEFAULT_CONFIG_STRING)
config.read([
        os.path.expanduser("~/.config/modlib"),
        ".modlib.config"
    ])


def storage_path(*paths):
    """
    Create a path inside the mods' storage directory
    """
    # abspath is used because the result could be used in symlinks
    return os.path.join(os.path.abspath(config.get("MODS", "directory")), *paths)


def packs_path(*paths):
    """
    Create a path inside the packs' storage directory
    """
    return os.path.join(config.get("PACKS", "directory"), *paths)


def valid_version(version):
    """
    Raise a ValueError if the argument is not a valid minecraft version.

    This function actually checks whether the input strings is made of positive
    integers seperated by dots. One could use regular expressions for a preciser
    match. But this is simpler, faster and should do fine enough.
    """
    # Custom int() only accepting natural numbers
    def nn(string):
        integer = int(string)
        if integer <= 0:
            raise ValueError(f"{string} is not a natural number")
        else:
            return integer

    # Check and return if correct
    try:
        list(map(nn, version.split(".")))
        return
    except ValueError:
        pass

    # The ValueError is outside the exception for cleaner error messages
    raise ValueError(f"{version} is not a proper minecraft version")

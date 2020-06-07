import os

from configparser import ConfigParser



config = ConfigParser()
config.DEFAULT = """
[MODS]
directory = ./storage

[PACKS]
directory = ./packs
use symlinks = True

[JSON]
ensure ascii = True
sort_keys = False
compact = False
"""
config.read_string(config.DEFAULT)
config.read([
        os.path.expanduser("~/.config/modlib"),
        ".modlib.config"
    ])


def json_config():
    """
    Get json.dump's kwargs from config
    """
    if config.getboolean("JSON", "compact", fallback=False):
        kwargs = {"seperators": (",", ":")}
    else:
        kwargs = {"indent": 4}
    kwargs["ensure_ascii"] = config.getboolean("JSON", "ensure ascii", fallback=True)
    kwargs["sort_keys"] = config.getboolean("JSON", "sort keys", fallback=False)
    return kwargs
config.JSON = json_config()

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



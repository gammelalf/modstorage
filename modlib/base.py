import os
import re

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


def valid_version(version: str) -> str:
    """
    Use a regex to check if the parameter looks anything like a minecraft version

    :param version: a string to check
    :type version: str
    :raises ValueError: when the string doesn't match the regex
    :return: the version (the unchanged parameter)
    :rtype: str
    """
    if re.match(r"1\.\d{1,2}\.\d{1,2}", version) is None:
        raise ValueError()
    else:
        return version

import os
import re

from .config import config


def storage_path(*paths: str) -> str:
    """
    Return the absolute path to something inside the storage dictionary.

    Use `os.path.join` on the input with the storage directory as defined in the config first.

    :param paths: paths to be joined
    :type paths: str
    :return: absolute path
    :rtype: str
    """
    # abspath is used because the result could be used in symlinks
    return os.path.join(os.path.abspath(config.get("MODS", "directory")), *paths)


def packs_path(*paths: str) -> str:
    """
    Return the path to something inside the packs dictionary.

    Use `os.path.join` on the input with the packs directory as defined in the config first.

    :param paths: paths to be joined
    :type paths: str
    :return: relative path
    :rtype: str
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

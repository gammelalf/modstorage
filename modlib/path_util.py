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

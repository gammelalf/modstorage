import typing
import os
from configparser import ConfigParser


class ModlibConfig(ConfigParser):
    """
    Config class for the modlib

    It initializes the default values and loads config files if it finds any.
    Config is loaded from ".config/modlib" in the users home directory
    or ".modlib.config" in the current working directory.
    """

    DEFAULT = """
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

    def __init__(self):
        super(ModlibConfig, self).__init__()
        self.read_string(ModlibConfig.DEFAULT)
        self.read([
            os.path.expanduser("~/.config/modlib"),
            ".modlib.config"
        ])

    @property
    def json(self) -> typing.Dict[str, typing.Any]:
        """
        Generate a keyword arguments dict for use in json.dump

        :return: kwargs dict for json.dump
        :rtype: typing.Dict[str, typing.Any]
        """
        if self.getboolean("JSON", "compact", fallback=False):
            kwargs = {"separators": (",", ":")}
        else:
            kwargs = {"indent": 4}
        kwargs["ensure_ascii"] = self.getboolean("JSON", "ensure ascii", fallback=True)
        kwargs["sort_keys"] = self.getboolean("JSON", "sort keys", fallback=False)
        return kwargs


config = ModlibConfig()

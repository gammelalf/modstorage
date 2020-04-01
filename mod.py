import os, json

import base


class Mod:

    __slots__ = ["__data__", "__name__"]
    __loaded__ = {}

    def new_mod(name):
        """
        Create new mod, its required files and return it
        """
        os.mkdir(base.storage_path(name))

        mod = object.__new__(Mod)
        mod.__data__ = {"default": {}, "versions": {}}
        mod.__name__ = name
        mod.write()

        return mod

    def __new__(cls, mod, *args):
        """
        Return loaded mod if loaded
        Create mod if not loaded
        """
        try:
            return Mod.__loaded__[mod]
        except:
            return super().__new__(cls)

    def __init__(self, mod):
        """
        Load data from mod.json
        """
        self.__name__ = mod
        with open(base.storage_path(self.__name__, "mod.json")) as f:
            self.__data__ = json.load(f)
        Mod.__loaded__[self.__name__] = self

    def __repr__(self):
        return f"Mod({self.__name__})"

    def get(self, key, version=None):
        if version is None:
            self.__data__["default"][key]
        else:
            self.__data__["versions"][version][key]

    def file(self, key, version=None):
        return base.storage_path(self.__name__, self.get(key, version))

    def write(self):
        with open(base.storage_path(self.__name__, "mod.json"), "w") as f:
            json.dump(self.__data__, f, indent=4)
    save = write

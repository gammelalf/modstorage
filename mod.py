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
        mod.__data__ = {"general": {}}
        mod.__name__ = name
        mod.write()

        Mod.__loaded__[mod.__name__] = mod
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
        with open(base.storage_pth(self.__name__, "mod.json")) as f:
            self.__data__ = json.load(f)
        Mod.__loaded__[self.__name__] = self

    def __repr__(self):
        return f"Mod({self.__name__})"

    def __dict__(self):
        return dict(self.__data__)

    def set(self, key, value, version=None):
        """
        Set an attribute value for a version.
        If no version is specified, it will be set in default.
        If the specified version doesn't exists yet, it will be created.
        """
        # Validate version
        base.valid_version(version)

        # Use specified version
        if version is not None:

            # Create version
            if version not in self.__data__:
                self.__data__[version] = {}

            # Set value
            self.__data__[version][key] = value

        # Set value to default
        else:
            self.__data__["general"][key] = value


    def get(self, key, version=None):
        """
        Get an version's attribute value
        If no version is specified or the versions does not have this attribute,
        it will use default's values.
        """
        # Validate version
        base.valid_version(version)

        # Specified version has the attribute
        if version is not None and key in self.__data__[version]:
            return self.__data__[version][key]

        # Use default
        else:
            return self.__data__["general"][key]


    def file(self, key, version=None):
        """
        Call get and join its return value to the path
        """
        return base.storage_path(self.__name__, self.get(key, version))


    def write(self):
        with open(base.storage_path(self.__name__, "mod.json"), "w") as f:
            json.dump(self.__data__, f, indent=4)
    save = write

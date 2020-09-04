import json
import os
import shutil
import typing

from .util import storage_path
from .util import valid_version
from .config import config


class Mod:
    """
    Class for mods

    Each mod is a singleton. This means two separately constructed objects with the same modid, will be the same object.
    The constructor just load existing mods (or returns the already loaded object),
    for creating new mods use the `new_mod` function.
    """

    __slots__ = ["__data__", "__modid__"]
    __loaded__ = {}

    @staticmethod
    def new_mod(modid: str) -> Mod:
        """
        Create new mod, its required files and return it

        :param modid: the mod's id
        :type modid: str
        :return: the new mod
        :rtype: Mod
        """
        os.mkdir(storage_path(modid))

        mod = object.__new__(Mod)
        mod.__data__ = {"general": {"dependencies": [], "name": modid}}
        mod.__modid__ = modid
        mod.write()

        Mod.__loaded__[mod.__modid__] = mod
        return mod

    def __new__(cls, modid, *args):
        """
        Return loaded mod if loaded
        Load mod if not loaded
        """
        try:
            return Mod.__loaded__[modid]
        except:
            return super().__new__(cls)

    def __init__(self, modid: str):
        """
        Load data from mod.json
        """
        self.__modid__ = modid
        with open(storage_path(self.__modid__, "mod.json")) as f:
            self.__data__ = json.load(f)
        Mod.__loaded__[self.__modid__] = self

    def __repr__(self):
        return f"Mod({self.__modid__})"

    def __str__(self):
        return self.__modid__

    def __dict__(self):
        return dict(self.__data__)

    def __getattr__(self, key):
        if key == "id":
            return self.__modid__
        else:
            return self.__getattribute__(key)
    
    def set(self, key: str, value: typing.Any, version: str = None) -> None:
        """
        Set an attribute value for a version
        If no version is specified, it will be set in default.
        If the specified version doesn't exists yet, it will be created.

        :param key: the key to set the value for
        :type key: str
        :param value: the value to set
        :type value: typing.Any
        :param version: the version in whose dict to set the value
        :type version: str [Optional]
        """
        # Use specified version
        if version is not None:

            # Validate version
            valid_version(version)

            # Create version if needed
            if version not in self.__data__:
                self.__data__[version] = {}

            # Set value
            self.__data__[version][key] = value

        # Set value to default
        else:
            self.__data__["general"][key] = value

    def get(self, key: str, version: str = None) -> typing.Any:
        """
        Get an version's attribute value
        If no version is specified or the versions does not have this attribute,
        it will use default's values.

        :param key: the key whose value to get
        :type key: str
        :param version: the versions from whose dict to get the value
        :type version: str
        :return: the key's corresponding value
        :rtype: typing.Any
        """
        # Specified version has the attribute
        if version is not None:

            # Validate version
            valid_version(version)

            if version in self.__data__ and key in self.__data__[version]:
                return self.__data__[version][key]

        # Didn't return yet? -> return the "general" value
        return self.__data__["general"][key]

    def file(self, key: str, version: str = None) -> str:
        """
        Call get() and join its return value to the storage's path

        :param key: the key whose file path to get
        :type key: str
        :param version: the versions from whose dict to get the file path
        :type version: str
        :return: the key's corresponding path
        :rtype: str
        """
        return storage_path(self.__modid__, self.get(key, version))

    def write(self):
        """
        Write the mod's dict to disk

        Same as save()
        """
        with open(storage_path(self.__modid__, "mod.json"), "w") as f:
            json.dump(self.__data__, f, **config.json)
    save = write

    def set_file(self, path, version):
        """
        Set the mod's file for a version

        This will move the given file into the mod's directory and create the symlink.

        :param path: current path to the file
        :type path: str
        :param version: the version the file is for
        :type version: str
        """
        # Validate version
        valid_version(version)

        # Get file's name
        name = os.path.basename(path)

        # Set the value's to be used with file()
        self.set("jar", name, version)
        self.set("link", f"{version}.jar", version)

        # Move the file
        shutil.move(path, self.file("jar", version))

        # Delete a possibly existing old link
        if os.path.lexists(self.file("link", version)): # exists() returns False on broken
            os.remove(self.file("link", version))       # symlinks. lexists() doesn't.

        # Link the file
        os.symlink(self.file("jar", version), self.file("link", version))

        # Save
        self.write()

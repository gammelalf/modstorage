import json   # load, dump
import os     # symlink, remove, path
import shutil # copy
import typing

from .version import Version
from .path_util import packs_path
from .config import config
from .mod import Mod

class Pack:
    """
    Class for packs

    Each pack is for a specific minecraft version and contains mods which must have a file for the pack's version.
    The pack the manages its mods' dependencies, adds missing ones and removes obsolete ones.

    :param file: the json file the pack stores its data in
    :type file: str
    :param directory: required for creating new packs; the directory the pack's mods are linked in
    :type directory: str [Optional]
    :param version: required for creating new packs; the version the pack is for
    :type version: str
    """

    def __init__(self, file: str, directory: str = None, version: Version = None):
        """
        Load a pack from its json file or create a new one
        """
        if os.path.exists(file):
            self.__file__ = file
        elif os.path.exists(packs_path(file)):
            self.__file__ = packs_path(file)
        elif directory is None:
            raise FileNotFoundError(file)
        else:
            self.__file__ = packs_path(file)

        # Just load existing pack
        if directory is None:
            with open(self.__file__) as f:
                self.__data__ = json.load(f)

        # Create new one
        else:
            # Init attributes
            self.__data__ = {"version": version, "directory": directory, "mods": {}}

            # Create json file
            self.write()

    def __getattr__(self, key: str) -> typing.Any:
        try:
            return self.__data__[key]
        except KeyError:
            return self.__getattribute__(key)

    def _mod_file(self, mod: Mod) -> str:
        """
        Get the path to a mod's file in the pack's directory

        :param mod: mod whose file to get
        :type mod: Mod
        :return: path to the mod's file
        :rtype: str
        """
        return os.path.join(self.directory, mod.get("name", self.version) + ".jar")

    def add(self, mod: Mod, manually: bool = True) -> None:
        """
        Add a mod and its dependencies to the pack

        :param mod: mod to add
        :type mod: Mod
        :param manually: whether the mod was added by the user or automatically added as dependency
        :type manually: bool
        """
        # Guarantee Mod instance
        if not isinstance(mod, Mod):
            mod = Mod(mod)

        # Check mod's version
        try:
            mod.get("link", self.version)
        except KeyError:
            raise RuntimeError(f"{mod} is not for version {self.version}")

        # Handle dependencies
        for dep in mod.get("dependencies", self.version):

            # Add missing dependencies
            if dep not in self.mods:
                self.add(dep, False)

            # Add mod to dependencies' dependants
            self.mods[dep]["dependants"].append(mod.id)

        # Create mod's file and entry
        if config.getboolean("PACKS", "use symlinks"):
            os.symlink(mod.file("link", self.version), self._mod_file(mod))
        else:
            shutil.copy(mod.file("jar", self.version), self._mod_file(mod))
        self.mods[mod.id] = {"manually": manually, "dependants": []}

        # Save
        self.write()

    def remove(self, mod: Mod) -> None:
        """
        Remove a mod from the pack

        This will raise an Exception if the mod is required for other mods.

        :param mod: the mod to remove
        :type mod: Mod
        """
        # Guarantee Mod instance
        if not isinstance(mod, Mod):
            mod = Mod(mod)

        # Check for errors
        if mod.id not in self.mods:
            raise RuntimeError(f"{mod} not in pack")
        if self.mods[mod.id]["dependants"] != []:
            raise RuntimeError(f"{mod} still has dependants")

        # Remove mod from dependencies' dependants
        for dep in mod.get("dependencies", self.version):
            self.mods[dep]["dependants"].remove(mod.id)

        # Remove link and entry
        os.remove(self._mod_file(mod))
        del self.mods[mod.id]

        # Save
        self.write()

    def autoremove(self) -> None:
        """
        Remove all mods not required for manually installed ones

        Its like apt's (debian's package manager) autoremove subcommand.
        """
        def single_autoremove() -> typing.List[Mod]:
            obsolete = []

            # Look for obsolete mods
            for name, data in self.mods.items():
                if not data["manually"] and data["dependants"] == []:
                    obsolete.append(name)

            # Delete them
            for mod in obsolete:
                self.remove(mod)

            # Return whether any mods where removed
            return obsolete != []

        # Call singe_remove() until it returns False
        # Which means no mods have been removed
        # Which means there are no obsolete mods left
        while single_autoremove():
            pass

    def write(self) -> None:
        """
        Write a pack to its json file
        """
        with open(self.__file__, "w") as f:
            json.dump(self.__data__, f, **config.json)
    save = write

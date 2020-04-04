import json, os

from base import valid_version
from mod import Mod

class Pack:

    def __init__(self, file, directory=None, version=None):
        """
        Load a pack from its json file or create a new one
        """
        self.__file__ = file

        # Just load existing pack
        if directory is None:
            with open(file) as f:
                self.__data__ = json.load(f)

        # Create new one
        else:
            # Validate version
            valid_version(version)

            # Init attributes
            self.__data__ = {"version": version, "directory": directory, "mods": {}}

            # Create json file
            self.write()


    def __getattr__(self, key):
        try:
            return self.__data__[key]
        except KeyError:
            return super().__getattr__(key)


    def __mod_file(self, mod):
        """
        Return the path to a mod's file in the pack's directory
        """
        return os.path.join(self.directory, mod.get("name", self.version) + ".jar")


    def add(self, mod, manually=True):
        """
        Add a mod and its dependencies to the pack
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
            self.mods[dep]["dependants"].append(mod.name)

        # Create link and the mod's entry
        os.symlink(mod.file("link", self.version), self.__mod_file(mod))
        self.mods[mod.name] = {"manually": manually, "dependants": []}

        # Save
        self.write()


    def remove(self, mod):
        """
        Remove a mod from the pack

        This will raise an Exception if the mod is required for other mods.
        """
        # Guarantee Mod instance
        if not isinstance(mod, Mod):
            mod = Mod(mod)

        # Check for errors
        if mod.name not in self.mods:
            raise RuntimeError(f"{mod} not in pack")
        if self.mods[mod.name]["dependants"] != []:
            raise RuntimeError(f"{mod} still has dependants")

        # Remove mod from dependencies' dependants
        for dep in mod.get("dependencies", self.version):
            self.mods[dep]["dependants"].remove(mod.name)

        # Remove link and entry
        os.remove(self.__mod_file(mod))
        del self.mods[mod.name]

        # Save
        self.write()


    def autoremove(self):
        """
        Remove all mods not required for manually installed ones
        """
        def single_autoremove():
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


    def write(self):
        """
        Write a pack to its json file
        """
        with open(self.__file__, "w") as f:
            json.dump(self.__data__, f, indent=4)
    save = write

import os, shutil, json

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
        mod.__data__ = {"general": {"dependencies": []}}
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
        with open(base.storage_path(self.__name__, "mod.json")) as f:
            self.__data__ = json.load(f)
        Mod.__loaded__[self.__name__] = self

    def __repr__(self):
        return f"Mod({self.__name__})"

    def __str__(self):
        return self.__name__

    def __dict__(self):
        return dict(self.__data__)
    
    def __getattr__(self, key):
        if key == "name":
            return self.__name__
        else:
            return super().__get__attr__(key)


    def set(self, key, value, version=None):
        """
        Set an attribute value for a version
        If no version is specified, it will be set in default.
        If the specified version doesn't exists yet, it will be created.
        """
        # Use specified version
        if version is not None:

            # Validate version
            base.valid_version(version)

            # Create version if needed
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
        # Specified version has the attribute
        if version is not None:

            # Validate version
            base.valid_version(version)

            if version in self.__data__ and key in self.__data__[version]:
                return self.__data__[version][key]

        # Didn't return yet? -> return the "general" value
        return self.__data__["general"][key]


    def file(self, key, version=None):
        """
        Call get() and join its return value to the path
        """
        return base.storage_path(self.__name__, self.get(key, version))


    def write(self):
        """
        Write the mod's dict to disk

        Same as save()
        """
        with open(base.storage_path(self.__name__, "mod.json"), "w") as f:
            json.dump(self.__data__, f, indent=4)
    save = write


    def set_file(self, path, version):
        """
        Set the mod's file for a version
        This will move the given file into the mod's directory
        and creates the symlink.
        """
        # Validate version
        base.valid_version(version)

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


    def link(self, version, destination):
        os.symlink(self.file("link", version), destination)


    def copy(self, version, destination):
        shutil.copy(self.file("jar", version), destination)

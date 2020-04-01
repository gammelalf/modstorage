import os

def storage_path(*paths):
    return os.path.join("./storage", *paths)

def valid_version(version):
    """
    Raise a ValueError if the argument is not a valid minecraft version
    """
    pass

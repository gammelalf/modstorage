import os

def storage_path(*paths):
    return os.path.join("./storage", *paths)

import re


class Version(str):
    """
    Class for minecraft versions

    It's just a string but with a regex check at construction.
    """

    PATTERN = re.compile(r"1\.\d{1,2}\.\d{1,2}")

    def __new__(cls, version: str):
        if not isinstance(version, str):
            raise TypeError(f"{repr(version)} is not a string")
        if Version.PATTERN.match(version) is None:
            raise ValueError(f"'{version}' doesn't match a version's regex")
        return str.__new__(cls, version)

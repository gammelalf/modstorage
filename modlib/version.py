import re


class Version(str):
    """
    Class for minecraft versions

    It's just a string but with a regex check at construction.
    This makes it interchangeable with normal strings and a lot of function which want versions will actual get
    strings because the strings will be stored to and read from json.

    So want is the point?
    Code outside this module should only give version objects as the type annotations demand to ensure no invalid
    versions are used. Once the string made it inside, it will be assumed to be a proper version.
    """

    PATTERN = re.compile(r"1\.\d{1,2}\.\d{1,2}")

    def __new__(cls, version: str):
        if not isinstance(version, str):
            raise TypeError(f"{repr(version)} is not a string")
        if Version.PATTERN.match(version) is None:
            raise ValueError(f"'{version}' doesn't match a version's regex")
        return str.__new__(cls, version)

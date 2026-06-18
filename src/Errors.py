class MapSyntaxError(Exception):
    """Raised when the map file contains invalid syntax."""
    pass


class PositiveInt(Exception):
    """Raised when a value expected to be a positive integer is invalid."""
    pass


class DuplicatConnection(Exception):
    """Raised when a duplicate connection is defined in the map."""
    pass


class DuplicatHub(Exception):
    """Raised when a hub is declared more than once."""
    pass


class DuplicatCoord(Exception):
    """Raised when multiple hubs share the same coordinates."""
    pass


class ZoneTypesError(Exception):
    """Raised when an unknown or invalid zone type is encountered."""
    pass


class UndefineHub(Exception):
    """Raised when a referenced hub does not exist in the map."""
    pass


class NoPathFinde(Exception):
    """Raised when no valid path can be found between start and end zones."""
    pass


class MapLogic(Exception):
    """Raised when the map structure violates logical validation rules."""
    pass

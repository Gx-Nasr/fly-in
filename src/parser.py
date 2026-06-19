import sys
from typing import Any, Dict, List, Set, Tuple
from .Errors import MapSyntaxError, PositiveInt, \
                    DuplicatHub, DuplicatCoord, MapLogic, \
                    ZoneTypesError, UndefineHub, DuplicatConnection


class Parser:
    """Parser for map files with hubs and connections.

    This parser loads a map definition from a file path, validates the
    syntax of drone count, hub declarations, and connection declarations,
    and builds an internal data dictionary for downstream use.
    """

    def __init__(self, path: str):
        """Initialize the parser with the given file path.

        Args:
            path: The path to the map file.
        """
        self.path: str = path
        self.data_dict: Dict[str, Any] = {
            "nb_drones": 0,
            "start_hub": {},
            "hubs": {},
            "end_hub": {},
            "connections": {}
        }

    @staticmethod
    def atopi(number: str) -> int:
        """Convert a string to a positive integer.

        Args:
            number: The string value to convert.

        Returns:
            The converted positive integer.

        Raises:
            PositiveInt: If the converted value is not a positive integer.
            MapSyntaxError: If the value is not an integer.
        """
        try:
            positive_number: int = int(number)
            if positive_number <= 0:
                raise PositiveInt()
        except ValueError:
            raise MapSyntaxError()
        return positive_number

    @staticmethod
    def parse_hubs_metadata(
        data_str: str, count_line: int, is_s_or_e: int = 0
            ) -> Dict[str, Any]:
        """Parse hub metadata from a zone declaration line.

        Args:
            data: The string content after the zone type label.
            count_line: The current line number for error reporting.

        Returns:
            A dictionary containing parsed hub metadata.
        """
        data: List[str] = data_str.split()

        if len(data) < 3:
            raise MapSyntaxError(
                f"Error in line {count_line}:"
                " Invalid zone declaration. Expected: <name> <x> <y>."
            )

        name = data[0]

        if "-" in name:
            raise MapSyntaxError(
                f"Error in line {count_line}:"
                " Zone names cannot contain '-'."
            )

        try:
            x = int(data[1])
            y = int(data[2])
        except ValueError:
            raise PositiveInt(
                f"Error in line {count_line}:"
                " Zone coordinates must be integers."
            )

        zone = "normal"
        color = None
        is_n_define = False
        max_drones = 1
        metadata: List[str] = data[3:]

        if metadata:
            if (
                not metadata[0].startswith("[")
                or not metadata[-1].endswith("]")
            ):
                raise MapSyntaxError(
                    f"Error in line {count_line}:"
                    " Metadata brackets are missing or malformed."
                )

            metadata[0] = metadata[0][1:]
            metadata[-1] = metadata[-1][:-1]

            used_keys: Set[str] = set()

            for item in metadata:
                data_val = item.split("=")

                if len(data_val) != 2:
                    raise MapSyntaxError(
                        f"Error in line {count_line}:"
                        " Invalid metadata syntax."
                    )

                key, value = data_val

                if key in used_keys:
                    raise MapSyntaxError(
                        f"Error in line {count_line}:"
                        f" Duplicate metadata key '{key}'."
                    )

                used_keys.add(key)

                if key == "color":
                    color = value

                elif key == "zone":
                    valid_types = {
                        "normal",
                        "blocked",
                        "restricted",
                        "priority"
                    }

                    if value not in valid_types:
                        raise ZoneTypesError(
                            f"Error in line {count_line}:"
                            f" Invalid zone type '{value}'"
                        )

                    zone = value

                elif key == "max_drones":
                    try:
                        max_drones = Parser.atopi(value)
                        is_n_define = True
                    except (MapSyntaxError, PositiveInt):
                        raise MapSyntaxError(
                            f"Error in line {count_line}:"
                            " max_drones must be a positive integer."
                        )
                else:
                    raise MapSyntaxError(
                        f"Error in line {count_line}:"
                        f" Unknown metadata key '{key}'"
                    )
        if is_s_or_e and is_n_define:
            if is_s_or_e > max_drones:
                raise MapLogic(
                    f"Error in line {count_line}:"
                    f" The start hub and end hub can't be less than nb_drones"
                )

        return {
            "name": name,
            "x": x,
            "y": y,
            "zone": zone,
            "color": color,
            "max_drones": max_drones
        }

    def define_hubs(self, data: List[str], count_line: int) -> int:
        """Parse hub declarations and update parser state.

        Args:
            data: Raw lines from the map file.
            count_line: Current line number after parsing nb_drones.

        Returns:
            Line number where connection parsing should start.

        Raises:
            MapSyntaxError: If the map syntax is invalid.
            DuplicatHub: If a hub is declared more than once.
            DuplicatCoord: If two hubs share the same coordinates.
            MapLogic: If the map violates logical constraints.
        """
        after_nb_drones = count_line
        start_flag = 0
        end_flag = 0

        hubs_names: Set[str] = set()
        coordinates: Set[Tuple[int, int]] = set()

        for line in data[after_nb_drones:]:
            count_line += 1
            clean_line = line.strip()

            if not clean_line:
                continue

            if "#" in clean_line:
                if clean_line.startswith("#"):
                    continue
                clean_line = clean_line.split("#")[0]

            split_line = clean_line.split(":")

            if len(split_line) != 2:
                raise MapSyntaxError(
                    f"Error in line {count_line}: Syntax Error"
                )

            if split_line[0] == "start_hub":
                if start_flag:
                    raise DuplicatHub(
                        f"Error in line {count_line}: "
                        "Multiple start zones are not allowed."
                    )

                start_flag += 1
                max_drones = self.data_dict["nb_drones"]

                self.data_dict["start_hub"] = self.parse_hubs_metadata(
                    split_line[1],
                    count_line,
                    is_s_or_e=max_drones
                )

                if self.data_dict["start_hub"]["zone"] == "blocked":
                    raise MapLogic(
                        f"Error in line {count_line}: "
                        "The start_hub cannot be blocked."
                    )

                start_name = self.data_dict["start_hub"]["name"]
                x = self.data_dict["start_hub"]["x"]
                y = self.data_dict["start_hub"]["y"]

                start_coord = (x, y)

                if start_coord in coordinates:
                    raise DuplicatCoord(
                        f"Error in line {count_line}: "
                        f"Coordinates ({x}, {y}) are already used "
                        "by another zone."
                    )

                if start_name in hubs_names:
                    raise DuplicatHub(
                        f"Error in line {count_line}: "
                        f"Zone '{start_name}' is already defined."
                    )

                hubs_names.add(start_name)
                coordinates.add(start_coord)

            elif split_line[0] == "end_hub":
                if end_flag:
                    raise DuplicatHub(
                        f"Error in line {count_line}: "
                        "Multiple end zones are not allowed."
                    )

                end_flag += 1

                max_drones = self.data_dict["nb_drones"]
                self.data_dict["end_hub"] = self.parse_hubs_metadata(
                    split_line[1],
                    count_line,
                    is_s_or_e=max_drones
                )

                if self.data_dict["end_hub"]["zone"] == "blocked":
                    raise MapLogic(
                        f"Error in line {count_line}: "
                        "The end_hub cannot be blocked."
                    )

                end_name = self.data_dict["end_hub"]["name"]
                x = self.data_dict["end_hub"]["x"]
                y = self.data_dict["end_hub"]["y"]

                end_coord = (x, y)

                if end_coord in coordinates:
                    raise DuplicatCoord(
                        f"Error in line {count_line}: "
                        f"Coordinates ({x}, {y}) are already used "
                        "by another zone."
                    )

                if end_name in hubs_names:
                    raise DuplicatHub(
                        f"Error in line {count_line}: "
                        f"Zone '{end_name}' is already defined."
                    )

                hubs_names.add(end_name)
                coordinates.add(end_coord)

            elif split_line[0] == "hub":
                hub_dict = self.parse_hubs_metadata(
                    split_line[1],
                    count_line,
                )

                name_hub = hub_dict["name"]
                x = hub_dict["x"]
                y = hub_dict["y"]

                hub_coord = (x, y)

                if hub_coord in coordinates:
                    raise DuplicatCoord(
                        f"Error in line {count_line}: "
                        f"Coordinates ({x}, {y}) are already used "
                        "by another zone."
                    )

                if name_hub in hubs_names:
                    raise DuplicatHub(
                        f"Error in line {count_line}: "
                        f"Zone '{name_hub}' is already defined."
                    )

                self.data_dict["hubs"][name_hub] = hub_dict

                hubs_names.add(name_hub)
                coordinates.add(hub_coord)

            elif split_line[0] == "connection":
                if not start_flag:
                    raise MapSyntaxError(
                        f"Error in line {count_line}: "
                        "Connections cannot be declared before "
                        "the start zone is defined."
                    )

                if not end_flag:
                    raise MapSyntaxError(
                        f"Error in line {count_line}: "
                        "Connections cannot be declared before "
                        "the end zone is defined."
                    )

                count_line -= 1
                break

            else:
                raise MapSyntaxError(
                    f"Error in line {count_line}: "
                    "Unknown declaration type."
                )

        if not start_flag:
            raise MapSyntaxError(
                "Error: Missing required start_hub declaration."
            )

        if not end_flag:
            raise MapSyntaxError(
                "Error: Missing required end_hub declaration."
            )

        return count_line

    @staticmethod
    def parse_connection_metadata(
        data_str: str, count_line: int
                                  ) -> Dict[str, Any]:
        """Parse connection metadata from a line.

        Args:
            data: The string content after the connection label.
            count_line: The current line number for error reporting.

        Returns:
            A dictionary containing the connection pair and capacity.
        """
        data: List[str] = data_str.split()

        if 1 > len(data) > 2:
            raise MapSyntaxError(
                f"Error in line {count_line}: Invalid connection declaration."
            )

        connection = data[0]

        if "-" not in connection:
            raise MapSyntaxError(
                f"Error in line {count_line}: Invalid connection syntax."
            )

        zones = connection.split("-")

        if len(zones) != 2:
            raise MapSyntaxError(
                f"Error in line {count_line}: Invalid connection syntax."
            )
        if zones[0] == zones[1]:
            raise MapSyntaxError(f"Error in line {count_line}:"
                                 " self connection is porhibited")
        max_link_capacity = 1

        metadata: List[str] = data[1:]
        metadata_len = len(metadata)
        if metadata_len > 1:
            raise MapSyntaxError(
                "Error in line {count_line}: Only 'max_link_capacity' "
                "metadata is allowed for connections."
            )

        if metadata_len:
            data_val = metadata[0].split("=")
            if len(data_val) != 2:
                raise MapSyntaxError(
                    "Error in line {count_line}: Invalid connection metadata "
                    "format. Expected: [max_link_capacity=<value>]."
                )

            if (
                not data_val[0].startswith("[")
                or not data_val[1].endswith("]")
                 ):
                raise MapSyntaxError(
                    f"Error in line {count_line}: "
                    "Metadata brackets are missing or malformed."
                )

            data_val[0] = data_val[0][1:]
            data_val[1] = data_val[1][:-1]

            if len(data_val) != 2:
                raise MapSyntaxError(
                    f"Error in line {count_line}: Invalid metadata syntax."
                )

            key, value = data_val

            if key == "max_link_capacity":
                try:
                    max_link_capacity = Parser.atopi(value)
                except (MapSyntaxError, PositiveInt):
                    raise MapSyntaxError(
                        f"Error in line {count_line}: "
                        "max_link_capacity must be a positive integer."
                    )

            else:
                raise MapSyntaxError(
                    f"Error in line {count_line}: "
                    f"Unknown metadata key '{key}'."
                )

        return {
            "connection": zones,
            "max_link_capacity": max_link_capacity
        }

    def define_connections(self, data: List[str], count_line: int) -> None:
        """Parse connection declarations and update parser state.

        Args:
            data: The raw lines of the map file.
            count_line: The current line number where connections begin.
        """
        valid_hubs: Set[str] = set()
        connections: Set[Tuple[str, str]] = set()
        counter = 0

        for hub_name in self.data_dict["hubs"]:
            valid_hubs.add(hub_name)

        valid_hubs.add(self.data_dict["start_hub"]["name"])
        valid_hubs.add(self.data_dict["end_hub"]["name"])

        after_hubs = count_line
        for line in data[after_hubs:]:
            count_line += 1
            clean_line = line.strip()
            if not clean_line:
                continue

            if "#" in clean_line:
                if clean_line.startswith("#"):
                    continue
                clean_line = clean_line.split("#")[0]

            split_line = clean_line.split(":")

            if len(split_line) != 2:
                raise MapSyntaxError(f"Error in line {count_line}:"
                                     " Syntax Error")

            if split_line[0] != "connection":
                raise MapSyntaxError(f"Error in line {count_line}:"
                                     " Syntax Error")

            metadata = self.parse_connection_metadata(
                split_line[1], count_line
                )

            if (
                metadata["connection"][0] not in valid_hubs
                or metadata["connection"][1] not in valid_hubs
            ):
                raise UndefineHub(
                    f"Error in line {count_line}: "
                    "Connection references an undefined zone."
                )

            z1, z2 = sorted(metadata["connection"])
            connection = (z1, z2)
            if connection in connections:
                raise DuplicatConnection(
                    f"Error in line {count_line}: Connection between "
                    f"'{z1}' and '{z2}' is already defined."
                )

            connections.add(connection)
            conn_id = "connection" + str(counter)
            self.data_dict["connections"][conn_id] = metadata
            counter += 1

    def initialize_data(self) -> List[str]:
        """Load and parse the map file content.

        Returns:
            The raw lines of the map file.
        """
        try:
            with open(self.path, "r") as file:
                data = file.read().splitlines()

        except (OSError, PermissionError):
            print(
                "Error: Unable to open the file. "
                "Please check the file path or permissions.",
                file=sys.stderr,
            )
            exit(1)

        count_line = 0
        nb_drones_flag = 0
        for line in data:
            count_line += 1
            clean_line = line.strip()
            if not clean_line:
                continue

            if "#" in clean_line:
                if clean_line.startswith("#"):
                    continue
                clean_line = clean_line.split("#")[0]

            nb_drones_line = clean_line.split(":")
            try:
                if nb_drones_line[0] != "nb_drones":
                    raise MapSyntaxError()
                self.data_dict["nb_drones"] = self.atopi(nb_drones_line[1])
                nb_drones_flag += 1
                break
            except (MapSyntaxError, PositiveInt):
                print(
                    f"Error in line {count_line}:"
                    " Invalid drone count declaration.",
                    file=sys.stderr,
                )
                print(
                    "Expected format: nb_drones:<positive_integer>",
                    file=sys.stderr,
                )
                exit(1)
        if not nb_drones_flag:
            raise MapSyntaxError(f"Error in line {count_line}"
                                 ": nb_drones are not defined.")
        count_line = self.define_hubs(data, count_line)
        self.define_connections(data, count_line)

        return data

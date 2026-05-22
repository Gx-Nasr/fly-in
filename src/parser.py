from typing import List
import json
import sys


class Parser:
    def __init__(self, path: str):
        self.path = path
        self.data = self.initialize_data()

    def initialize_data(self) -> List[str]:
        try:
            with open(self.path, "r") as file:
                data = file.read()
                data = [line.strip() for line in data.split("\n") if line.strip()]

        except (OSError, PermissionError):
            print(
                "Error: Unable to open the file. "
                "Please check the file path or permissions.",
                file=sys.stderr
            )
            exit(1)

        cleaned_lines = []

        for line in data:
            if "#" in line:
                new_line = line.split("#")
                line = new_line[0]
                if not new_line[0]:
                    continue
                if ":" not in new_line[0]:
                    print(f"Invalid syntax in this line :{new_line[0]} # {new_line[1]}")
                    exit(1)
            cleaned_lines.append(line)

        if len(cleaned_lines) < 4:
            print(
                "The map file must contain at least "
                "'nb_drones', 'start_hub', "
                "'end_hub', and one connection between them.",
                file=sys.stderr
            )
            exit(1)

        data_dict = {}
        data_dict["nb_drones"] = self.parse_number_of_drones(cleaned_lines)

        data_dict.update(
            self.parse_hubs(cleaned_lines)
        )

        return data_dict

    def parse_number_of_drones(self, data):
        drones_line = data[0]

        if "nb_drones:" not in drones_line:
            print(
                "Error in line 1: "
                "The map file must start with 'nb_drones'.",
                file=sys.stderr
            )
            exit(1)

        try:
            drones = int(drones_line.split(":")[1])

            if drones <= 0:
                raise ValueError

        except ValueError:
            print(
                "Error in line 1: nb_drones must be a positive integer",
                file=sys.stderr
            )
            exit(1)

        return drones

    def get_metadata(self, data, max_drones_value=0):
        data = data.split()

        name = data[0]
        x = int(data[1])
        y = int(data[2])

        zone = "normal"
        color = None

        if max_drones_value:
            max_drones = max_drones_value
        else:
            max_drones = 1

        metadata = data[3:]

        if len(metadata) > 0:

            if (
                metadata[0].startswith("[")
                and metadata[-1].endswith("]")
            ):
                metadata[0] = metadata[0][1:]
                metadata[-1] = metadata[-1][:-1]

                for index, item in enumerate(metadata):
                    metadata[index] = item.split("=")

                    key = metadata[index][0]
                    value = metadata[index][1]

                    if key == "color":
                        color = value

                    elif key == "zone":
                        zone = value

                    elif key == "max_drones":
                        max_drones = int(value)

                        if max_drones <= 0:
                            raise ValueError(
                                "The value of 'max_drones' "
                                "must be a positive integer."
                            )

                    else:
                        raise SyntaxError(
                            "Invalid metadata syntax."
                        )

            else:
                raise SyntaxError(
                    "Metadata brackets are missing or malformed."
                )

        return {
            "name": name,
            "x": x,
            "y": y,
            "zone": zone,
            "color": color,
            "max_drones": max_drones
        }

    def parse_connection_data(self, data, defined_zones):
        data = data.split()

        connection = data[0].split("-", 1)

        max_link_capacity = 1

        if len(connection) != 2:
            raise ValueError(
                "A connection must contain exactly two zones."
            )

        if (
            connection[0] not in defined_zones
            or connection[1] not in defined_zones
        ):
            raise ValueError(
                "Connection contains an undefined zone."
            )

        data_length = len(data)

        if data_length == 1:
            return {
                "connection": connection,
                "max_link_capacity": max_link_capacity
            }

        metadata = data[1].split("=")

        if (
            not metadata[0].startswith("[")
            or not metadata[1].endswith("]")
        ):
            raise SyntaxError(
                "Invalid connection metadata brackets."
            )

        metadata[0] = metadata[0][1:]
        metadata[1] = metadata[1][:-1]

        if (
            metadata[0] != "max_link_capacity"
            or len(metadata) != 2
        ):
            raise SyntaxError(
                "Only 'max_link_capacity' is allowed "
                "in connection metadata."
            )

        try:
            max_link_capacity = int(metadata[1])

            if max_link_capacity <= 0:
                raise ValueError

        except ValueError:
            raise ValueError(
                "max_link_capacity must be a positive integer"
            )

        return {
            "connection": connection,
            "max_link_capacity": max_link_capacity
        }

    def parse_hubs(self, data):
        valid_zone_types = [
            "blocked",
            "normal",
            "restricted",
            "priority"
        ]

        coordinates_list = []

        hub_dict = {}

        index = 1

        start_hub = data[index].split(":", 1)
        start_hub_name = start_hub[0]
        if start_hub_name != "start_hub":
            print(
                "Error: After 'nb_drones', the map must start with a 'start_hub' definition.",
                file=sys.stderr
            )
            exit(1)

        number_of_drones = int(
            data[0].split(":", 1)[1]
        )

        hub_dict[start_hub_name] = self.get_metadata(
            start_hub[1],
            number_of_drones
        )

        if (hub_dict[start_hub_name]["max_drones"] < number_of_drones):
            print(
                "max_drones in start hub "
                "must be >= nb_drones", file=sys.stderr
            )
            exit(1)

        if (hub_dict[start_hub_name]["zone"] not in valid_zone_types):
            print(
                "Zone type must be one of: "
                "['blocked', 'normal', 'restricted', 'priority']", file=sys.stderr
            )
            exit(1)

        index += 1
        data_length = len(data)
        hub_dict["hubs"] = {}

        coordinates = (
            hub_dict[start_hub_name]["x"],
            hub_dict[start_hub_name]["y"]
        )
        coordinates_list.append(coordinates)

        defined_zones = [
            hub_dict[start_hub_name]["name"]
        ]
        e_n_d = 0
        while index < data_length:
            hub = data[index].split(":", 1)

            if hub[0] != "hub":

                if hub[0] == "end_hub":
                    e_n_d = 1
                    hub_dict[hub[0]] = self.get_metadata(hub[1])
                    max_drones = hub_dict[hub[0]]["max_drones"]
                    zone_name = hub_dict[hub[0]]["zone"]
                    if (max_drones < number_of_drones):
                        print("max_drones in end hub must be >= nb_drones",
                              file=sys.stderr
                        )
                        exit(1)

                    if (zone_name not in valid_zone_types):
                        print(
                            "Zone type must be one of: "
                            "['blocked', 'normal', 'restricted', 'priority']",
                            file=sys.stderr
                        )
                        exit(1)

                    coordinates = (
                        hub_dict[hub[0]]["x"],
                        hub_dict[hub[0]]["y"]
                    )

                    if coordinates in coordinates_list:
                        print("Duplicate coordinates", file=sys.stderr)
                        exit(1)

                    coordinates_list.append(coordinates)
                    defined_zones.append(
                        hub_dict[hub[0]]["name"]
                    )

                    index += 1
                    continue
                else:
                    break

            hub_data = self.get_metadata(hub[1])

            if (hub_data["zone"] not in valid_zone_types):
                print(
                    "Zone type must be one of: "
                    "['blocked', 'normal', 'restricted', 'priority']",
                    file=sys.stderr
                )
                exit(1)

            coordinates = (
                hub_data["x"],
                hub_data["y"]
            )

            if coordinates in coordinates_list:
                print("Duplicate coordinates", file=sys.stderr)
                exit(1)

            coordinates_list.append(coordinates)
            name = hub_data["name"]
            defined_zones.append(name)

            hub_dict["hubs"][name] = hub_data

            index += 1
        if not e_n_d:
            print("Error: end_hub are missde")
            exit(1)
        hub_dict["connections"] = {}

        connection_id = 0

        while index < data_length:
            connection = data[index].split(":", 1)

            if connection[0] != "connection":
                print(
                    "Invalid connection definition syntax.",
                    file=sys.stderr
                )
                exit(1)

            if len(connection) != 2:
                print(
                    "A connection definition must contain "
                    "exactly one ':'.",
                    file=sys.stderr
                )
                exit(1)

            try:
                hub_dict["connections"][
                    "connection" + str(connection_id)
                ] = self.parse_connection_data(
                    connection[1],
                    defined_zones
                )

            except (ValueError, SyntaxError) as error:
                print(
                    f"Error in line {index + 1}: {error}",
                    file=sys.stderr
                )
                exit(1)

            except BaseException:
                print(
                    f"Error in line {index + 1}: "
                    "Invalid syntax format.",
                    file=sys.stderr
                )
                exit(1)

            connection_id += 1
            index += 1

        return hub_dict


parser = Parser(sys.argv[1])

with open("test.json", "w") as file:
    json.dump(parser.data, file, indent=4)
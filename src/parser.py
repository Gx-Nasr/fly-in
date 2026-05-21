from typing import List
from custem_errors import BracketsError
import json
import sys


class Parser:
    def __init__(self, path: str):
        self.path = path
        self.data = self.data_init()

    def data_init(self) -> List[str]:
        try:
            with open(self.path, "r") as f:
                data = f.read()
                data = [line.strip() for line in data.split("\n")
                        if line.strip()]

        except (OSError, PermissionError):
            print("Error: Unable to open the file. Please check the file path or permissions.", file=sys.stderr)
            exit(1)

        i = 0
        great_lines = []
        for line in data:
            if "#" in line:
                line = line.split("#")[0]
                if not line or ":" not in line:
                    continue
            great_lines.append(line)
            i += 1
        if len(great_lines) < 4:
            print(
                "The map file must contain at least 'nb_drones', "
                "'start_hub', 'end_hub', and one connection between them.",
                file=sys.stderr
            )
            exit(1)
    
        data_dict = {}
        data_dict["nb_drones"] = self.number_of_drones(great_lines)
        data_dict.update(self.parse_hub(great_lines))
        

        return data_dict

    def number_of_drones(self, data):
        drones = data[0]
        if "nb_drones:" not in drones:
            print("Error in line 1: The map file must start with 'nb_drones'.", file=sys.stderr)
            exit(1)
        try:
            drones = int(drones.split(":")[1])
            if drones <= 0:
                raise ValueError
        except ValueError:
            print("nb_drones must be a positive integer", file=sys.stderr)
            exit(1)

        return drones

    def get_meta_data(self, data, s_or_e=0):
        data = data.split()
        name = data[0]
        x = int(data[1])
        y = int(data[2])
        zone = "normal"
        color = None
        if s_or_e:
            max_drones = s_or_e
        else:
            max_drones = 1
        data = data[3:]
        if len(data) > 0:
            if data[0].startswith('[') and data[-1].endswith(']'):
                data[0] = data[0][1:]
                data[-1] = data[-1][:-1]
                i = 0
                for s in data:
                    data[i] = s.split("=")
                    if data[i][0] == "color":
                        color = data[i][1]
                    elif data[i][0] == "zone":
                        zone = data[i][1]
                    elif data[i][0] == "max_drones":
                        max_drones = int(data[i][1])
                        if max_drones <= 0:
                            raise ValueError("The value of 'max_drones' must be a positive integer.")
                    else:
                        raise SyntaxError("Invalid metadata syntax.")
                    i += 1

            else:
                raise BracketsError("Metadata brackets are missing or malformed.")

        return {
                "name": name,
                "x": x, "y": y,
                "zone": zone,
                "color": color,
                "max_drones": max_drones
                }


    def connection_data(self, data, definde_zones):
        data = data.split()
        connect = data[0].split("-", 1)
        max_link_capacity = 1
        if len(connect) != 2:
            raise ValueError("A connection must contain exactly two zones.")
        if connect[0] not in definde_zones or connect[1] not in definde_zones:
            raise ValueError("Connection contains an undefined zone.")
        data_len = len(data)
        if data_len == 1:
            return {"connection": connect,
                    "max_link_capacity": max_link_capacity}
        else:
            m_data = data[1].split("=")
            if not m_data[0].startswith("[") or not m_data[1].endswith("]"):
                raise SyntaxError("Invalid connection metadata brackets.")
            m_data[0] = m_data[0][1:]
            m_data[1] = m_data[1][:-1]
            if m_data[0] != "max_link_capacity" or len(m_data) != 2:
                raise SyntaxError("Only 'max_link_capacity' is allowed in connection metadata.")
            try:
                max_link_capacity = int(m_data[1])
                if max_link_capacity <= 0:
                    raise ValueError
            except ValueError:
                raise ValueError("max_link_capacity must be a positive integer")
            return {"connection": connect,
                    "max_link_capacity": max_link_capacity}


    def parse_hub(self, data):
        list_of_zones_type = ["blocked", "normal", "restricted", "priority"]
        hub_dict = {}
        i = 1
        start_hub = data[i].split(":", 1)
        if start_hub[0] != "start_hub":
            print("Error: After 'nb_drones', the map must start with a 'start_hub' definition.", file=sys.stderr)
            exit(1)
        nb_drones = int(data[0].split(":")[1])
        hub_dict[start_hub[0]] = self.get_meta_data(start_hub[i], nb_drones)
        if hub_dict[start_hub[0]]["max_drones"] < nb_drones:
            raise ValueError("max_drones in start hub must be >= nb_drons")
        if hub_dict[start_hub[0]]["max_drones"] not in list_of_zones_type:
            raise SyntaxError("zone typ must be defined like this : ['blocked', 'normal', 'restricted', 'priority']")
        i += 1
        list_len = len(data)
        hub_dict["hubs"] = {}
        definde_zones = [hub_dict[start_hub[0]]["name"]]
        while i < list_len:
            hub = data[i].split(":", 1)
            hub[0] = hub[0]
            if hub[0] != "hub":
                if hub[0] == "end_hub":
                    hub_dict[hub[0]] = self.get_meta_data(hub[1])
                    if hub_dict[hub[0]]["max_drones"] < nb_drones:
                        raise ValueError("max_drones in end hub must be >= nb_drons")
                    if hub_dict[hub[0]]["zone"] not in list_of_zones_type:
                        raise SyntaxError("zone typ must be defined like this : ['blocked', 'normal', 'restricted', 'priority']")
                    definde_zones.append(hub_dict[hub[0]]["name"])
                    i += 1
                    break
                else:
                    print(f"Error in line {i+1}: Invalid hub definition syntax.", file=sys.stderr)
                    exit(1)
            hub_data = self.get_meta_data(hub[1])
            if hub_data["zone"] not in list_of_zones_type:
                raise SyntaxError("zone typ must be defined like this : ['blocked', 'normal', 'restricted', 'priority']")
            name = hub_data.pop("name")
            definde_zones.append(name)
            hub_dict["hubs"][name] = hub_data
            i += 1
        hub_dict["connections"] = {}
        id = 0
        while i < list_len:
            connetc = data[i].split(":", 1)
            if connetc[0] != "connection":
                print("Invalid connection definition syntax.", file=sys.stderr)
                exit(1)
            if len(connetc) != 2:
                print("A connection definition must contain exactly one ':'.", file=sys.stderr)
                exit(1)
            try:
                hub_dict["connections"]["connection"+str(id)] = self.connection_data(connetc[1], definde_zones)
            except (ValueError, SyntaxError) as e:
                print(f"Error in line {i+1}: {e}", file=sys.stderr)
                exit(1)
            except BaseException:
                print(f"Error in line {i+1}: Invalid syntax format.", file=sys.stderr)
                exit(1)
            id += 1
            i += 1

        return hub_dict


d  = Parser(sys.argv[1])

with open("test.json", "w") as f:
    json.dump(d.data, f, indent=4)
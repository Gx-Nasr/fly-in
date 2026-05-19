from typing import List
from custem_errors import BracketsError


class Parser:
    def __init__(self, path: str):
        self.path = path
        self.data = self.read_data_from_file()
        self.nb_drones = self.numbre_of_drones()
        self.hub_dict = self.parse_hub()

    def read_data_from_file(self) -> List[str]:
        try:
            with open(self.path, "r") as f:
                data = f.read()
                data = [line.strip() for line in data.split("\n")
                        if line.strip()]

        except (OSError, PermissionError):
            print("Error: Unable to open the file. Please check the "
                  "file name or permissions.")
            exit(1)

        i = 0
        great_lines = []
        for line in data:
            if "#" in line:
                line = line.split("#")[0].strip()
                if not line or ":" not in line:
                    continue
            great_lines.append(line)
            i += 1
        return great_lines

    def numbre_of_drones(self):
        drones = self.data[0]
        if "nb_drones" not in drones:
            print("Error in line 1: The map file must start with the number of"
                  " drones.")
            exit(1)
        try:
            drones = int(drones.split(":")[1])
            if drones <= 0:
                raise ValueError()
        except ValueError:
            print("Error in line 1: The value after 'nb_drones' must be an "
                  "integer and positive.")
            exit(1)

        return drones

    def get_meta_data(self, data):
        data = data.split()
        name = data[0].strip()
        x = int(data[1])
        y = int(data[2])
        zone = "normal"
        color = None
        max_drones = 1
        data = data[3:]
        if len(data) > 0:
            if data[0].startswith('[') and data[-1].endswith(']'):
                data[0] = data[0].replace("[", "")
                data[-1] = data[-1].replace("]", "")
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
                            raise ValueError("max droms must be positive")
                    else:
                        raise SyntaxError("invalid syntax")
                    i += 1

            else:
                raise BracketsError("Invalid brackets")

        return {
                "name": name,
                "x": x, "y": y,
                "zone": zone,
                "color": color,
                "max_drones": max_drones
                }


    def parse_hub(self):
        hub_dict = {}
        i = 1
        start_hub = self.data[i].split(":")
        if start_hub[0].strip() != "start_hub":
            print(
                "Error: After 'nb_drones', the map must define hubs "
                "and start with a 'start_hub'."
            )
            exit(1)
        hub_dict[start_hub[0]] = self.get_meta_data(start_hub[i])
        i += 1
        list_len = len(self.data)
        hub_dict["hubs"] = {}
        while i < list_len:
            hub = self.data[i].split(":")
            hub[0] = hub[0].strip()
            if hub[0] != "hub":
                if hub[0] == "end_hub":
                    hub_dict[hub[0]] = self.get_meta_data(hub[1])
                    break
                else:
                    raise SyntaxError("Invalid syntax")
            hub_data = self.get_meta_data(hub[1])
            name = hub_data.pop("name")
            hub_dict["hubs"][name] = hub_data
            i += 1
        
        return hub_dict







d = Parser("../maps/challenger/01_the_impossible_dream.txt")
# print(d.hub_dict)

for x, y in d.hub_dict.items():
    print(x)
    print()
    for n, m in y.items():
        print(n)
        print(m)
        print()
    print()

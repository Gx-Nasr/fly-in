from typing import List


class Parser:
    def __init__(self, path: str):
        self.path = path
        self.data = self.read_data_from_file()
        self.nb_drones = self.numbre_of_drones()

    def read_data_from_file(self) -> List[str]:
        try:
            with open(self.path, "r") as f:
                data = f.read()
                data = data.split("\n")
        except (OSError, PermissionError):
            print("Sorry we can't open the, check the file name or permision")
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
        drones = -1
        for line in self.data:
            if "nb_drones" in line:
                line = line.split(":")
                drones = int(line[1])
                break
        if drones == -1:
            print("Invalid data in nb_drones")
            exit(1)

        return drones


d = Parser("../maps/hard/02_capacity_hell.txt")
for c in d.data:
    print(c)

print(d.nb_drones)

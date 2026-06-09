from typing import List
from dataclasses import dataclass, field


@dataclass
class Zone:
    name: str
    x: int
    y: int
    zone_type: str
    color: str | None
    max_drones: int
    current_drones: int = 0




@dataclass
class Connection:
    from_zone: Zone
    to_zone: Zone
    max_link_capacity: int


@dataclass
class Drone:
    id_drone: int
    current_zone: Zone
    path: dict[int, Zone] = field(default_factory=dict)

@dataclass
class GraphData:
    nb_drones: int
    all_drones: List[Drone]
    zones_dict: dict[str, Zone]
    connections: List[Connection]
    start: Zone
    end: Zone
    turns: int = 0


    def move_cost(self, zone):
        if zone.zone_type == "restricted":
            return 2
        return 1


    def get_neighbor(self, connection, zone):
        if connection.from_zone == zone:
            return connection.to_zone
        return connection.from_zone

    def get_connections(self, zone):
        neighbors = []
        for connect in self.connections:
            if zone == connect.from_zone:
                neighbors.append(connect)

            elif zone == connect.to_zone:
                neighbors.append(connect)

        return neighbors

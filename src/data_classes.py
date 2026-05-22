from dataclasses import dataclass


@dataclass
class Drone:
    nb_drons: int
    drone_id: int
    zone: str
    is_transit: bool


@dataclass
class Zone:
    """
    name: str
    x: int
    y: int
    zone_type: str
    color: str
    max_drones: int
    drones: int
    """

    name: str
    x: int
    y: int
    zone_type: str
    color: str
    max_drones: int
    drones: int

@dataclass
class Connection:
    zone1: Zone
    zone2: Zone
    max_link_capacity: int


@dataclass
class Graph:
    zones: dict[str, Zone]
    adjacency: dict[str, list[tuple[Zone, Connection]]]  # هنا الneighbors
    start: Zone
    end: Zone
    nb_drones: int
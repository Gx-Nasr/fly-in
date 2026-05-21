from dataclasses import dataclass


@dataclass
class Drone:
    nb_drons: int
    drone_id: int
    zone: str
    is_transit: bool
    

@dataclass
class connection:
    from_: str
    to: str
    max_link_capacity: int



@dataclass
class zone:
    name: str
    x: int 
    y: int
    type: str
    color: str
    max_drones: int
    neighbors: dict[str, connection]

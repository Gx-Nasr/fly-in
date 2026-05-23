import json
from data_classes import Zone, Drone, Connection, GraphData

data_dict = {
    "nb_drones": 5,
    "start_hub": {
        "name": "start",
        "x": 0,
        "y": 0,
        "zone": "normal",
        "color": "green",
        "max_drones": 5
    },
    "hubs": {
        "junction": {
            "name": "junction",
            "x": 1,
            "y": 0,
            "zone": "normal",
            "color": "yellow",
            "max_drones": 1
        },
        "dead_end": {
            "name": "dead_end",
            "x": 1,
            "y": 1,
            "zone": "normal",
            "color": "red",
            "max_drones": 1
        },
        "correct_path": {
            "name": "correct_path",
            "x": 2,
            "y": 0,
            "zone": "normal",
            "color": "blue",
            "max_drones": 1
        },
        "intermediate": {
            "name": "intermediate",
            "x": 3,
            "y": 0,
            "zone": "normal",
            "color": "blue",
            "max_drones": 1
        }
    },
    "end_hub": {
        "name": "goal",
        "x": 4,
        "y": 0,
        "zone": "normal",
        "color": "green",
        "max_drones": 5
    },
    "connections": {
        "connection0": {
            "connection": [
                "start",
                "junction"
            ],
            "max_link_capacity": 1
        },
        "connection1": {
            "connection": [
                "junction",
                "dead_end"
            ],
            "max_link_capacity": 1
        },
        "connection2": {
            "connection": [
                "junction",
                "correct_path"
            ],
            "max_link_capacity": 1
        },
        "connection3": {
            "connection": [
                "correct_path",
                "intermediate"
            ],
            "max_link_capacity": 1
        },
        "connection4": {
            "connection": [
                "intermediate",
                "goal"
            ],
            "max_link_capacity": 1
        }
    }
}


class GraphInit:
    def __init__(self, data_dict):
        self.graph = self.creat_graph(data_dict)

    def creat_zone(self, zone_data):
        name = zone_data["name"]
        x = zone_data["x"]
        y = zone_data["y"]
        zone_type = zone_data["zone"]
        color = zone_data["color"]
        max_drones = zone_data["max_drones"]

        return Zone(name, x, y, zone_type, color, max_drones)
    
    def creat_connection(self, connection_data, zones):
        from_zone = connection_data["connection"][0]
        to_zone = connection_data["connection"][1]
        max_link_capacity = connection_data["max_link_capacity"]
        for zone in zones.values():
            if zone.name == from_zone:
                from_zone = zone
                break

        for zone in zones.values():
            if zone.name == to_zone:
                to_zone = zone
                break

        return Connection(from_zone, to_zone, max_link_capacity)


    def creat_graph(self, data_dict):
        zones = {}
        nb_drones = data_dict["nb_drones"]
        start_zone = self.creat_zone(data_dict["start_hub"])
        start_zone.current_drones = nb_drones
        zones[start_zone.name] = start_zone
        for zone in data_dict["hubs"].values():
            zone = self.creat_zone(zone)
            zones[zone.name] = zone
        end_zone = self.creat_zone(data_dict["end_hub"])
        zones[end_zone.name] = end_zone

        connections = []
        for v in data_dict["connections"].values():
            connections.append(self.creat_connection(v, zones))

        drones = []
        for n in range(data_dict["nb_drones"]):
            drone = Drone(n, zones[start_zone.name])
            drones.append(drone)
        
        game_data = GraphData(nb_drones, drones, zones, connections, start_zone, end_zone)


        return game_data

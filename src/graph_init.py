from .data_classes import Zone, Drone, Connection, GraphData


class GraphInit:
    """Initialize and build the graph structure from parsed input data."""

    def __init__(self, data_dict: dict) -> None:
        """Create a graph from the provided data dictionary.

        Args:
            data_dict: Parsed map data containing zones, connections,
                drones, start hub, and end hub information.
        """
        self.graph: GraphData = self.creat_graph(data_dict)

    def creat_zone(
        self,
        zone_data: dict,
        drones: int = 0,
    ) -> Zone:
        """Create a Zone instance from zone data.

        Args:
            zone_data: Dictionary containing zone attributes.
            drones: Number of drones currently located in the zone.

        Returns:
            A populated Zone object.
        """
        name: str = zone_data["name"]
        x: int = zone_data["x"]
        y: int = zone_data["y"]
        zone_type: str = zone_data["zone"]
        color: str | None = zone_data["color"]
        max_drones: int = zone_data["max_drones"]

        return Zone(
            name,
            x,
            y,
            zone_type,
            color,
            max_drones,
            drones,
        )

    def creat_connection(
        self,
        connection_data: dict,
        zones: dict[str, Zone],
    ) -> Connection:
        """Create a Connection object between two zones.

        Args:
            connection_data: Dictionary describing the connection.
            zones: Dictionary of all available zones indexed by name.

        Returns:
            A Connection instance linking two zones.
        """
        from_zone: str | Zone = connection_data["connection"][0]
        to_zone: str | Zone = connection_data["connection"][1]
        max_link_capacity: int = connection_data["max_link_capacity"]

        for zone in zones.values():
            if zone.name == from_zone:
                from_zone = zone
                break

        for zone in zones.values():
            if zone.name == to_zone:
                to_zone = zone
                break

        return Connection(
            from_zone,
            to_zone,
            max_link_capacity,
        )

    def creat_graph(
        self,
        data_dict: dict,
    ) -> GraphData:
        """Build the complete graph structure.

        Creates all zones, connections, drones, and wraps them inside
        a GraphData object.

        Args:
            data_dict: Parsed map data.

        Returns:
            Fully initialized GraphData instance.
        """
        zones: dict[str, Zone] = {}

        nb_drones: int = data_dict["nb_drones"]

        start_zone: Zone = self.creat_zone(
            data_dict["start_hub"],
            nb_drones,
        )
        zones[start_zone.name] = start_zone

        for zone in data_dict["hubs"].values():
            zone = self.creat_zone(zone)
            zones[zone.name] = zone

        end_zone: Zone = self.creat_zone(
            data_dict["end_hub"]
        )
        zones[end_zone.name] = end_zone

        connections: list[Connection] = []
        for connection_data in data_dict["connections"].values():
            connections.append(
                self.creat_connection(
                    connection_data,
                    zones,
                )
            )

        drones: list[Drone] = []
        for n in range(data_dict["nb_drones"]):
            drone: Drone = Drone(
                n,
                zones[start_zone.name],
            )
            drones.append(drone)

        game_data: GraphData = GraphData(
            nb_drones,
            drones,
            zones,
            connections,
            start_zone,
            end_zone,
        )

        return game_data
import heapq
from typing import Dict, List, Optional, Set, Tuple
from Errors import NoPathFinde
from data_classes import Connection, Drone, GraphData, Zone


class PathFinding:
    """Perform pathfinding with reservation-aware graph traversal."""

    def __init__(self, graph: GraphData) -> None:
        """Initialize the pathfinding engine.

        Args:
            graph: GraphData containing zones, connections, and drones.
        """
        self.graph: GraphData = graph
        self.start: Zone = graph.start
        self.end: Zone = graph.end
        self.zone_reservations: Dict[Tuple[str, int], int] = {}
        self.capacity_reservations: Dict[Tuple[str, str, int], int] = {}

    def has_path(self) -> bool:
        """Check whether a path exists from the start zone to the end zone.

        Returns True if the end zone is reachable, otherwise False.
        """
        stack = [self.start]
        visited = []

        while stack:
            current_zone = stack.pop()

            if current_zone == self.end:
                return True

            if current_zone.name in visited:
                continue

            visited.append(current_zone.name)

            for connection in self.graph.get_connections(current_zone):

                neighbor = self.graph.get_neighbor(
                    connection,
                    current_zone
                )

                if neighbor.zone_type == "blocked":
                    continue

                if neighbor.name not in visited:
                    stack.append(neighbor)

        return False

    def are_valid_neighbors(
            self, connections: List[Connection], zone: Zone, if_s: int = 0
            ) -> bool:

        nb_blocked: int = 0
        for connection in connections:
            neighbor = self.graph.get_neighbor(connection, zone)
            if neighbor.zone_type == "blocked":
                nb_blocked += 1
        nb_connections = len(connections) - if_s

        if nb_blocked == nb_connections:
            return False
        return True

    def dijkstra(self) -> Optional[List[Tuple[Zone, int]]]:
        """Compute the next valid path from start to end.

        The Dijkstra search is adapted to account for waiting in zones,
        zone capacity reservations, and connection capacity reservations.

        Returns:
            A list of (zone, turn) tuples representing the path, or None if no
            path exists.
        """
        turn: int = 0
        distances: Dict[Tuple[Zone, int], int] = {}
        parent: Dict[Tuple[Zone, int], Optional[Tuple[Zone, int]]] = {}
        pq: List[Tuple[int, int, int, Tuple[Zone, int]]] = []
        counter: int = 0

        start_state: Tuple[Zone, int] = (self.start, turn)
        distances[start_state] = turn
        parent[start_state] = None
        heapq.heappush(pq, (turn, 0, counter, start_state))
        visitions: Set[Tuple[Zone, int]] = set()
        while pq:
            _, _1, _2, state = heapq.heappop(pq)
            current_zone, current_turn = state

            if state in visitions:
                continue
            visitions.add(state)

            if current_zone == self.graph.end:
                path: List[Tuple[Zone, int]] = []

                backtrack_state: Optional[Tuple[Zone, int]] = state
                old_turn: int = state[1]
                old_state: Tuple[Zone, int] = state

                while backtrack_state is not None:
                    current_state: Tuple[Zone, int] = backtrack_state

                    if old_turn == current_state[1] + 2:
                        path.append(old_state)

                    path.append(current_state)

                    old_turn = current_state[1]
                    old_state = current_state
                    backtrack_state = parent[current_state]

                path.reverse()
                return path

            connections: List[Connection] = (
                self.graph.get_connections(current_zone)
            )

            wait_turn: int = current_turn + 1
            n = 0
            if state[0] != self.start:
                n = 1
            if (
                self.are_valid_neighbors(connections, state[0], n)
                and len(connections) - n != 0
            ):
                wait_state: Tuple[Zone, int] = (
                    current_zone,
                    wait_turn
                )

                if distances.get(wait_state, -1) == -1:
                    distances[wait_state] = wait_turn
                    parent[wait_state] = state
                    counter += 1
                    heapq.heappush(
                        pq,
                        (wait_turn, 1, counter, wait_state)
                    )
            else:
                object.__setattr__(state[0], "zone_type", "blocked")

            for connection in connections:
                neighbor: Zone = self.graph.get_neighbor(
                    connection,
                    current_zone
                )

                if neighbor.zone_type == "blocked":
                    continue

                cost: int = self.graph.move_cost(neighbor)
                turns: int = current_turn + cost

                if neighbor != self.end:
                    current_reserved: int = (
                        self.zone_reservations.get(
                            (neighbor.name, turns),
                            0
                        )
                    )

                    if current_reserved >= neighbor.max_drones:
                        continue

                is_capacity_full: bool = False

                z1: str
                z2: str
                z1, z2 = tuple(
                    sorted(
                        [
                            current_zone.name,
                            neighbor.name
                        ]
                    )
                )

                for t in range(current_turn, turns):
                    conn_reserverd: int = (
                        self.capacity_reservations.get(
                            (z1, z2, t),
                            0
                        )
                    )

                    if (
                        conn_reserverd
                        >= connection.max_link_capacity
                    ):
                        is_capacity_full = True
                        break

                if is_capacity_full:
                    continue

                next_state: Tuple[Zone, int] = (
                    neighbor,
                    turns
                )

                if distances.get(next_state, -1) == -1:
                    distances[next_state] = turns
                    parent[next_state] = state

                    zone_cost: int = 0

                    if neighbor.zone_type == "priority":
                        zone_cost = -1

                    counter += 1

                    heapq.heappush(
                        pq,
                        (
                            turns,
                            zone_cost,
                            counter,
                            next_state
                        )
                    )

        return None

    def reserve(self, path: List[Tuple[Zone, int]]) -> None:
        """Reserve zone and connection capacity for a computed path.

        Args:
            path: List of (zone, turn) tuples describing the drone path.
        """
        current_zone: Zone | int = 0
        current_turn: int = 0
        path_len = len(path)
        for i in range(path_len):
            if (current_zone, current_turn) != path[i]:
                current_zone, current_turn = path[i]

                if current_zone != self.start and current_zone != self.end:
                    self.zone_reservations[
                        (current_zone.name, current_turn)
                    ] = self.zone_reservations.get(
                        (current_zone.name, current_turn), 0
                    ) + 1

                if i < path_len - 1:
                    next_zone, next_turn = path[i + 1]

                    if current_zone.name != next_zone.name:
                        z1, z2 = tuple(
                            sorted([current_zone.name, next_zone.name])
                        )

                        for t in range(current_turn, next_turn):
                            self.capacity_reservations[
                                (z1, z2, t)
                            ] = self.capacity_reservations.get(
                                (z1, z2, t), 0
                            ) + 1

    def print_output(self, drones: List[Drone]) -> int:
        """Print drone movements for each turn.

        Args:
            drones: List of Drone objects containing computed paths.
        """
        max_turn: int = 0
        check_list: Dict[int, Zone] = {}
        for drone in drones:
            path_len: int = len(drone.path)
            if path_len > max_turn:
                max_turn = path_len
            check_list[drone.id_drone] = drone.path[0][0]

        for t in range(1, max_turn):
            for drone in drones:
                drone_len: int = len(drone.path)
                if t < drone_len:
                    if check_list[drone.id_drone] != drone.path[t][0]:
                        if (
                            t + 1 < drone_len
                            and drone.path[t + 1] == drone.path[t]
                        ):
                            print(
                                f"D{drone.id_drone+1}-"
                                f"{drone.path[t-1][0].name}-"
                                f"{drone.path[t][0].name}",
                                end=" ",
                            )
                        else:
                            print(
                                f"D{drone.id_drone+1}-{drone.path[t][0].name}",
                                end=" ",
                            )
                            check_list[drone.id_drone] = drone.path[t][0]
            print()
        return max_turn

    def get_drones_path(self) -> None:
        """Compute and reserve paths for all drones."""
        if not self.has_path():
            raise NoPathFinde(
                "We can't find the path check your map are valid"
            )

        for drone in self.graph.all_drones:
            path = self.dijkstra()

            if path is None:
                raise NoPathFinde(
                    "We can't find the path check your map are valid"
                )

            drone.path = path
            self.reserve(path)

        self.graph.turns = self.print_output(
            self.graph.all_drones
        )

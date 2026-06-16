from __future__ import annotations

import heapq
from typing import Dict, List, Optional, Set, Tuple

from .data_classes import Connection, Drone, GraphData, Zone


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
                old_turn: int = state[1]
                old_state: Tuple[Zone, int] = state
                while state is not None:
                    if old_turn == state[1] + 2:
                        path.append(old_state)
                    path.append(state)
                    old_turn = state[1]
                    old_state = state
                    state = parent[state]
                path.reverse()
                return path

            wait_turn: int = current_turn + 1
            if (
                current_zone == self.start
                or self.zone_reservations.get(
                    (current_zone.name, wait_turn), 0
                    ) < current_zone.max_drones
            ):
                wait_state: Tuple[Zone, int] = (current_zone, wait_turn)

                if distances.get(wait_state, -1) == -1:
                    distances[wait_state] = wait_turn
                    parent[wait_state] = state
                    counter += 1
                    heapq.heappush(pq, (wait_turn, 1, counter, wait_state))

            connections: List[Connection] = self.graph.get_connections(
                current_zone
                )

            for connection in connections:
                neighbor: Zone = self.graph.get_neighbor(
                    connection, current_zone
                    )

                if neighbor.zone_type == "blocked":
                    continue

                cost: int = self.graph.move_cost(neighbor)
                turns: int = current_turn + cost

                if neighbor != self.end:
                    current_reserved: int = self.zone_reservations.get(
                        (neighbor.name, turns), 0
                    )
                    if current_reserved >= neighbor.max_drones:
                        continue

                is_capacity_full: bool = False
                z1: str
                z2: str
                z1, z2 = tuple(sorted([current_zone.name, neighbor.name]))
                for t in range(current_turn, turns):
                    conn_reserverd: int = self.capacity_reservations.get(
                        (z1, z2, t), 0
                    )
                    if conn_reserverd >= connection.max_link_capacity:
                        is_capacity_full = True
                        break

                if is_capacity_full:
                    continue

                next_state: Tuple[Zone, int] = (neighbor, turns)

                if distances.get(next_state, -1) == -1:
                    distances[next_state] = turns
                    parent[next_state] = state
                    zone_cost: int = 0
                    if neighbor.zone_type == "priority":
                        zone_cost = -1
                    counter += 1
                    heapq.heappush(pq, (turns, zone_cost, counter, next_state))
        return None

    def reserve(self, path: List[Tuple[Zone, int]]) -> None:
        """Reserve zone and connection capacity for a computed path.

        Args:
            path: List of (zone, turn) tuples describing the drone path.
        """
        current_zone: Zone | int = 0
        current_turn: int = 0
        for i in range(len(path)):
            if (current_zone, current_turn) != path[i]:
                current_zone, current_turn = path[i]

                if current_zone != self.start and current_zone != self.end:
                    self.zone_reservations[
                        (current_zone.name, current_turn)
                    ] = self.zone_reservations.get(
                        (current_zone.name, current_turn), 0
                    ) + 1

                if i < len(path) - 1:
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

    def print_output(self, drones: List[Drone]) -> None:
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

    def get_drones_path(self) -> None:
        """Compute and reserve paths for all drones, then print the result.

        Raises:
            ValueError: If a path cannot be found for a drone.
        """
        for drone in self.graph.all_drones:
            path = self.dijkstra()
            if not path:
                raise ValueError(
                    "We can't find the path check your map are valid"
                )

            drone.path = path
            self.reserve(path)

        self.print_output(self.graph.all_drones)

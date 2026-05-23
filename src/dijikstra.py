from data_classes import GraphData
import heapq


class Dijkstra:
    def __init__(self, graph: GraphData):
        self.graph = graph

    def get_zone_cost(self, zone):

        if zone.zone_type == "blocked":
            return float("inf")

        elif zone.zone_type == "restricted":
            return 2

        elif zone.zone_type == "priority":
            return 0.5

        return 1

    def get_other_zone(self, connection, current_zone):

        if connection.from_zone == current_zone:
            return connection.to_zone

        return connection.from_zone

    def shortest_path(self, start_zone, end_zone):

        distances = {}
        previous = {}

        for zone in self.graph.zones_dict.values():
            distances[zone.name] = float("inf")
            previous[zone.name] = None

        distances[start_zone.name] = 0

        priority_queue = []
        heapq.heappush(priority_queue, (0, start_zone.name))

        visited = set()

        while priority_queue:

            current_distance, current_zone_name = heapq.heappop(priority_queue)

            if current_zone_name in visited:
                continue

            visited.add(current_zone_name)

            current_zone = self.graph.zones_dict[current_zone_name]

            if current_zone == end_zone:
                break

            connections = self.graph.get_connections(current_zone)

            for connection in connections:

                neighbor = self.get_other_zone(connection, current_zone)

                if neighbor.zone_type == "blocked":
                    continue

                move_cost = self.get_zone_cost(neighbor)

                new_distance = current_distance + move_cost

                if new_distance < distances[neighbor.name]:

                    distances[neighbor.name] = new_distance

                    previous[neighbor.name] = current_zone.name

                    heapq.heappush(
                        priority_queue,
                        (new_distance, neighbor.name)
                    )

        path = []

        current = end_zone.name

        while current is not None:
            path.append(current)
            current = previous[current]

        path.reverse()

        if path[0] != start_zone.name:
            return []

        return path

    def assign_paths_to_drones(self):

        for drone in self.graph.all_drones:

            path = self.shortest_path(
                drone.current_zone,
                self.graph.end
            )

            drone.path = path
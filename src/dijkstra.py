from data_classes import GraphData
import heapq


class PathFinding:
    def __init__(self, graph):
        self.graph: GraphData = graph
        self.start = self.graph.start
        self.end = self.graph.end
        self.zone_reservations = {}
        self.capacity_reservations = {}


    def dijkstra(self):
        turn = 0
        distances = {}
        parent = {}
        pq = []

        start_state = (self.start, turn)
        distances[start_state] = turn
        parent[start_state] = None
        heapq.heappush(pq, (turn, start_state))
        visitions = set()


        while pq:
            all_turns, state = heapq.heappop(pq)
            current_zone, current_turn = state

            if state in visitions:
                continue
            visitions.add(state)

            if current_zone == self.graph.end:
                path = []
                zone = state
                while zone is not None:
                    path.append(zone)
                    zone = parent[zone]
                path.reverse()
                return path

            wait_turn = current_turn + 1
            if current_zone == self.start or self.zone_reservations.get((current_zone.name, wait_turn), 0) < current_zone.max_drones:
                wait_state = (current_zone, wait_turn)

                if distances.get(wait_state, -1) == -1:
                    distances[wait_state] = wait_turn
                    parent[wait_state] = state
                    heapq.heappush(pq, (wait_turn, wait_state))

            connections = self.graph.get_connections(current_zone)
            for connection in connections:
                neighbor = self.graph.get_neighbor(connection, current_zone)
                cost = self.graph.move_cost(neighbor)
                turns = current_turn + cost

                if neighbor != self.end:
                    current_reserved = self.zone_reservations.get((neighbor.name, turns), 0)
                    if current_reserved >= neighbor.max_drones:
                        continue

                is_capacity_full = False
                z1, z2 = sorted([current_zone.name, neighbor.name])
                for t in range(current_turn, turns):
                    conn_reserverd = self.capacity_reservations.get((z1, z2, t), 0)
                    if conn_reserverd >= connection.max_link_capacity:
                        is_capacity_full = True
                        break

                if is_capacity_full:
                    continue

                next_state = (neighbor, turns)

                if distances.get(next_state, -1) == -1:
                    distances[next_state] = turns
                    parent[next_state] = state
                    heapq.heappush(pq, (turns, next_state))
        return []

    def reserve(self, path):
        for i in range(len(path)):
            current_zone, current_turn = path[i]

            if current_zone != self.start and current_zone != self.end:
                self.zone_reservations[(current_zone.name, current_turn)] = self.zone_reservations.get((current_zone.name, current_turn), 0) + 1

            if i < len(path) - 1:
                next_zone, next_turn = path[i + 1]

                if current_zone.name != next_zone.name:
                    z1, z2 = sorted([current_zone.name, next_zone.name])

                    for t in range(current_turn, next_turn):
                        self.capacity_reservations[(z1, z2, t)] = self.capacity_reservations.get((z1, z2, t), 0) + 1



    def get_drones_path(self):

        for drone in self.graph.all_drones:
            path = self.dijkstra()
            if not path:
                raise ValueError("We can't find the path check your map are valid")

            for t in path:
                zone, turn = t
                drone.path[turn] = zone

            self.reserve(path)

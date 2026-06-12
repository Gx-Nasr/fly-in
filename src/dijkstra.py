from .data_classes import GraphData
import heapq
import json


class PathFinding:
    def __init__(self, graph):
        self.graph: GraphData = graph
        self.start = graph.start
        self.end = graph.end
        self.zone_reservations = {}
        self.capacity_reservations = {}


    def dijkstra(self):
        turn = 0
        distances = {}
        parent = {}
        pq = []
        counter = 0

        start_state = (self.start, turn)
        distances[start_state] = turn
        parent[start_state] = None
        heapq.heappush(pq, (turn, 0, counter,start_state))
        visitions = set()


        while pq:
            _, _1, _2, state = heapq.heappop(pq)
            current_zone, current_turn = state

            if state in visitions:
                continue
            visitions.add(state)

            if current_zone == self.graph.end:
                path = []
                old_turn = state[1]
                while state is not None:
                    if old_turn == state[1] + 2:
                        path.append(old_state)
                    path.append(state)
                    old_turn = state[1]
                    old_state = state
                    state = parent[state]
                path.reverse()
                return path

            wait_turn = current_turn + 1
            if current_zone == self.start or self.zone_reservations.get((current_zone.name, wait_turn), 0) < current_zone.max_drones:
                wait_state = (current_zone, wait_turn)

                if distances.get(wait_state, -1) == -1:
                    distances[wait_state] = wait_turn
                    parent[wait_state] = state
                    counter += 1
                    heapq.heappush(pq, (wait_turn, 1, counter, wait_state))

            connections = self.graph.get_connections(current_zone)
            for connection in connections:
                neighbor = self.graph.get_neighbor(connection, current_zone)

                if neighbor.zone_type == "blocked":
                    continue

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
                    zone_cost = 0
                    if neighbor.zone_type == "priority":
                        zone_cost = -1
                    counter += 1
                    heapq.heappush(pq, (turns, zone_cost, counter,next_state))
        return None


    def reserve(self, path):
        current_zone, current_turn = (0, 0)
        for i in range(len(path)):
            if (current_zone, current_turn) != path[i]:
                current_zone, current_turn = path[i]

                if current_zone != self.start and current_zone != self.end:
                    self.zone_reservations[(current_zone.name, current_turn)] = self.zone_reservations.get((current_zone.name, current_turn), 0) + 1

                if i < len(path) - 1:
                    next_zone, next_turn = path[i + 1]

                    if current_zone.name != next_zone.name:
                        z1, z2 = sorted([current_zone.name, next_zone.name])

                        for t in range(current_turn, next_turn):
                            self.capacity_reservations[(z1, z2, t)] = self.capacity_reservations.get((z1, z2, t), 0) + 1


    def print_output(self, drones):
        max_turn = 0
        check_list = {}
        for drone in drones:
            path_len = len(drone.path)
            if path_len > max_turn:
                max_turn = path_len
            check_list[drone.id_drone] = drone.path[0][0]

        for t in range(1, max_turn):
            for drone in drones:
                drone_len = len(drone.path)
                if t < drone_len:
                    if check_list[drone.id_drone] != drone.path[t][0]:
                        if t + 1 < drone_len and drone.path[t+1] == drone.path[t]:
                            print(f"D{drone.id_drone+1}-{drone.path[t-1][0].name}-{drone.path[t][0].name}", end=" ")
                        else:
                            print(f"D{drone.id_drone+1}-{drone.path[t][0].name}", end=" ")
                            check_list[drone.id_drone] = drone.path[t][0]
            print()

    def get_drones_path(self):

        for drone in self.graph.all_drones:
            path = self.dijkstra()
            if not path:
                raise ValueError("We can't find the path check your map are valid")

            drone.path = path
            self.reserve(path)

        self.print_output(self.graph.all_drones)

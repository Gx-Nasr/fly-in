from parser import Parser
from graph_init import GraphInit
from dijkstra import PathFinding
import sys
from visualization import DroneVisualizer


class Fly_In:
    def __init__(self, file_path: str):
        self.path: str = file_path

    def run(self) -> None:
        parser = Parser(self.path)
        try:
            parser.initialize_data()
            graph: GraphInit = GraphInit(parser.data_dict)
            djikstra = PathFinding(graph.graph)
            djikstra.get_drones_path()
            vis = DroneVisualizer(graph.graph)
            vis.show()
        except Exception as e:
            print(e, file=sys.stderr)
            exit(1)


if __name__ == "__main__":
    fly_in = Fly_In(sys.argv[1])
    fly_in.run()

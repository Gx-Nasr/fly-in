from .parser import Parser
from .graph_init import GraphInit
from .dijkstra import PathFinding
import sys
from .Errors import MapSyntaxError
from .visualization import DroneVisualizer


parser = Parser(sys.argv[1])
try:
    parser.initialize_data()
except Exception as e:
    print(e)


graph = GraphInit(parser.data_dict)

djikstra = PathFinding(graph.graph)

djikstra.get_drones_path()

vis = DroneVisualizer(graph.graph)
vis.show()

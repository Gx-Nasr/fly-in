from .parser import Parser
from .graph_init import GraphInit
from .dijkstra import PathFinding
import sys
import json
from .Errors import *

parser = Parser(sys.argv[1])
try:
    parser.initialize_data()
except MapSyntaxError as e:
    print(e)


graph = GraphInit(parser.data_dict)

djikstra = PathFinding(graph.graph)

djikstra.get_drones_path()

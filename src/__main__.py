from .parser import Parser
from .graph_init import GraphInit
from .dijkstra import PathFinding
import sys
import json

parser = Parser(sys.argv[1])

with open("test.json", "w") as file:
    json.dump(parser.data, file, indent=4)

graph = GraphInit(parser.data)

djikstra = PathFinding(graph.graph)

djikstra.get_drones_path()

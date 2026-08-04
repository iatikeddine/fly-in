from Parsing import Parsing
from Graph import Graph, Zone
from typing import List, Dict, Union, Any
from Path import Algorithm
from Simulation import Simulation
from Printer import ColoredPrint
from argparse import ArgumentParser
import sys


if __name__ == "__main__":
    try:
        arg_parser: ArgumentParser = ArgumentParser()
        arg_parser.add_argument("path")
        arg = arg_parser.parse_args()
        parser: Parsing = Parsing()
        parser.process_file(arg.path)
        zones: Dict[str, Dict[str, Any]] = parser.zones
        connections: Dict[str, Union[None, int]] = parser.connections
        graph: Graph = Graph()
        all_zones: List[Zone] = graph.create_zones(zones)
        graph.add_zones(all_zones)
        graph.connect_graph(connections)
        start_hub: str = graph.get_start_hub_name()
        algo: Algorithm = Algorithm(graph.zones[start_hub], graph)
        first_path: List[str] = algo.Dijkstra()
        second_path: List[str] = algo.second_shortest_path(first_path)
        printer: ColoredPrint = ColoredPrint()
        sim = Simulation(
            graph, first_path, second_path, parser.nb_drones, printer)
        sim.init_drones()
        sim.start_simulation()
    except ValueError as e:
        sys.exit(f"{e}")
    except FileNotFoundError:
        sys.exit("Error: the given file does not exist")
    except IsADirectoryError:
        sys.exit("Error: the given path is a directory")
    except PermissionError:
        sys.exit("Error: file does not have the necessary permission")

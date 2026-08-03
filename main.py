from Parsing import Parsing
from Graph import Graph, Zone
from typing import List, Dict, Union
from Path_finding import Algorithm
from Simulation import Simulation
from printer import ColoredPrint


if __name__ == "__main__":
    try:
        parser = Parsing()
        parser.process_file("maps/medium/02_circular_loop.txt")
        zones: Dict = parser.zones
        connections: Dict[str, Union[None, int]] = parser.connections
        graph: Graph = Graph()
        all_zones: List[Zone] = graph.create_zones(zones)
        graph.add_zones(all_zones)
        graph.connect_graph(connections)
        start_hub = graph.get_start_hub_name()
        algo = Algorithm(graph.zones[start_hub], graph)
        first_path = algo.Dijkstra()
        second_path = first_path
        print(first_path)
        print(second_path)
        printer: ColoredPrint = ColoredPrint()
        sim = Simulation(
            graph, first_path, second_path, parser.nb_drones, printer)
        sim.init_drones()
        sim.start_simulation()
    except FileNotFoundError:
        print("Error: the given file does not exist")
    except IsADirectoryError:
        print("Error: the given path is a directory")
    except PermissionError:
        print("Error: file does not have the necessary permission")

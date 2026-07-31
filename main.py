from parsing import Parsing
from Graph import Graph, Zone
from typing import List, Dict, Union
from Path_finding import Algorithm
from Simulation import Simulation


if __name__ == "__main__":
    try:
        parser = Parsing()
        parser.process_file("maps/challenger/01_the_impossible_dream.txt")
        zones: Dict = parser.zones
        connections: Dict[str, Union[None, int]] = parser.connections
        graph: Graph = Graph()
        all_zones: List[Zone] = graph.create_zones(zones)
        graph.add_zones(all_zones)
        graph.connect_graph(connections)
        start_hub = graph.get_start_hub_name()
        algo = Algorithm(graph.zones[start_hub], graph)
        path = algo.Dijkstra()
        print(path)
        sim = Simulation(graph, path, parser.nb_drones)
        sim.init_drones()
        sim.start_simulation()
    except FileNotFoundError:
        print("Error: the given file does not exist")
    except IsADirectoryError:
        print("Error: the given path is a directory")
    except PermissionError:
        print("Error: file does not have the necessary permission")

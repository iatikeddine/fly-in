from parsing import Parsing
from Graph import Graph, Zone
from typing import List, Dict, Union


if __name__ == "__main__":
    try:
        parser = Parsing()
        parser.process_file("map.txt")
        zones: Dict = parser.zones
        connections: Dict[str, Union[None, int]] = parser.connections
        graph: Graph = Graph()
        all_zones: List[Zone] = graph.create_zones(zones)
        graph.add_zones(all_zones)
        graph.connect_graph(connections)
        for zone, zone_object in graph.zones.items():
            print(f"{zone}: {zone_object.connections}")
    except ValueError as e:
        print(e)
    except FileNotFoundError:
        print("Error: the given file does not exist")
    except IsADirectoryError:
        print("Error: the given path is a directory")
    except PermissionError:
        print("Error: file does not have the necessary permission")

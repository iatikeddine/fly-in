from typing import List
from Graph import Graph, Zone, Connection
from Drone import Drone


class Simulation:
    def __init__(self, graph: Graph, path: List[str], nb_drones: int):
        self.graph: Graph = graph
        self.path: List[str] = path
        self.nb_drones: int = nb_drones
        self.drones: List[Drone] = []

    def init_drones(self) -> None:
        for x in range(self.nb_drones):
            self.drones.append(Drone(x))

    def check_connection_status(self, current: Zone, next: Zone) -> int:
        connection: Connection = current.get_connection(next)
        if connection.current_stat < connection.capacity:
            return connection.capacity - connection.current_stat
        return -1

    def check_zone_status(self, zone: Zone) -> int:
        if zone.current_size < zone.max_drones:
            return zone.max_drones - zone.current_size
        return -1

    def turns_needed(self, curren_zone: Zone, next_zone: Zone) -> int:
        connetion: Connection = curren_zone.get_connection(next_zone)
        weight: int = connetion.weight
        if weight == 100 or weight == 199:
            return 1
        elif weight == 200:
            return 2

    def start_simulation(self) -> None:
        end_hub_name: str = self.graph.get_end_hub_name()
        end_hub_zone: Zone = self.graph.zones[end_hub_name]
        object_path: List[Zone] = [
            self.nb_drones[name]
            for name in self.path
        ]
        while end_hub_zone.current_size != self.nb_drones:
            for x in range(len(object_path)):
                current_zone: Zone = object_path[x]
                if current_zone.current_size > 0 and current_zone is not object_path[-1]:
                    next_zone: Zone = object_path[x + 1]
                    connection_availability: int = self.check_connection_status(
                        current_zone, next_zone
                    )
                    zone_availability: int = self.check_zone_status(next_zone)
                    turns_needed: int = self.turns_needed(
                        current_zone, next_zone
                    )
                    moves_count: int = 0
                    if connection_availability == zone_availability:
                        moves_count = zone_availability
                    else:
                        moves_count = min(zone_availability,
                                          connection_availability)
                    for x in range(moves_count):
                        pass

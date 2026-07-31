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
            self.drones.append(Drone(x, self.graph))

    def check_connection_status(self, current: Zone, next_zone: Zone) -> int:
        connection: Connection = current.get_connection(next_zone)
        if connection.current_stat < connection.capacity:
            return connection.capacity - connection.current_stat
        return 0

    def check_zone_status(self, zone: Zone) -> int:
        if zone.current_size < zone.max_drones:
            return zone.max_drones - zone.current_size
        return 0

    def fetch_drones_in_zone(self, zone: Zone) -> List:
        drones_in_zone: List = []
        for drone in self.drones:
            if drone.current_position is zone:
                drones_in_zone.append(drone)
        return drones_in_zone

    def fetch_drones_in_connection(
            self, connection: Connection
    ) -> List[Drone]:
        drones_in_connection: List[Drone] = []
        for drone in self.drones:
            if (
                drone.current_position is connection
                and drone.been_in_connection
            ):
                drones_in_connection.append(drone)
        for drone in self.drone:
            if (
                drone.current_position is connection
                and not drone.been_in_connection
            ):
                drones_in_connection.append(drone)
        return drones_in_connection

    def move_drones_in_connection(
            self, connection: Connection,
            to_zone: Zone
    ) -> None:
        if connection.weight != 200:
            return None
        if connection.current_stat == 0:
            return None
        drones_in_connection: List[Drone] = self.fetch_drones_in_connection(
            connection)
        places_available_in_zone: int = self.check_zone_status(to_zone)
        i: int = 0
        for drone in drones_in_connection:
            if i == places_available_in_zone:
                break
            drone.move_to_zone(to_zone)
            i += 1

    def moves_drones_in_zone(
            self, current_zone: Zone,
            next_zone: Zone, connection: Connection
    ) -> None:
        drones_in_zone: List[Drone] = self.fetch_drones_in_zone(current_zone)
        if connection.weight == 200:
            places_available: int = self.check_connection_status(connection)
            if places_available == 0:
                return None
            else:
                i: int = 0
                for drone in drones_in_zone:
                    if i == places_available:
                        break
                    drone.move_to_connection(connection)
                    i += 1
        else:
            places_available: int = self.check_zone_status(next_zone)
            if places_available == 0:
                return None
            i = 0
            for drone in drones_in_zone:
                if i == places_available:
                    break
                drone.move_to_zone(next_zone)
                i += 1

    def start_simulation(self) -> None:
        end_hub_name: str = self.graph.get_end_hub_name()
        end_hub_zone: Zone = self.graph.zones[end_hub_name]
        object_path: List[Zone] = [
            self.graph.zones[name]
            for name in self.path
        ]
        while end_hub_zone.current_size != self.nb_drones:
            turn: int = len(object_path)
            for x in range(turn):
                current: Zone = object_path[x]
                if current is not object_path[-1]:
                    next_zone: Zone = object_path[x + 1]
                    connection: Connection = current.get_connection(next_zone)
                    self.move_drones_in_connection(connection, next_zone)
                    self.moves_drones_in_zone(current, next_zone, connection)

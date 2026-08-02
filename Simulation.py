from typing import List
from Graph import Graph, Zone, Connection
from Drone import Drone
from printer import ColoredPrint


class Simulation:
    def __init__(
            self,
            graph: Graph,
            path_1: List[str],
            path_2: List[str],
            nb_drones: int,
            printer: ColoredPrint
    ) -> None:
        self.graph: Graph = graph
        self.path_1: List[Zone] = [graph.zones[name] for name in path_1]
        self.path_2: List[str] = [graph.zones[name] for name in path_2]
        self.nb_drones: int = nb_drones
        self.drones: List[Drone] = []
        self.printer = printer

    def init_drones(self) -> None:
        for x in range(self.nb_drones):
            self.drones.append(Drone(
                x, self.graph, self.path_1, self.path_2)
            )

    def check_connection_status(self, current: Zone, next_zone: Zone) -> int:
        connection: Connection = current.get_connection(next_zone)
        if connection.current_size < connection.capacity:
            return connection.capacity - connection.current_size

        return 0

    def check_zone_status(self, zone: Zone) -> int:
        if zone.kind == "end_hub":
            return self.nb_drones
        if zone.current_size < zone.max_drones:
            return zone.max_drones - zone.current_size

        return 0

    def fetch_drones_in_zone(
            self,
            zone: Zone,
            current_path: List[Zone]
    ) -> List:
        drones_in_zone: List = []
        for drone in self.drones:
            if drone.current_position is zone and drone.path == current_path:
                drones_in_zone.append(drone)

        return drones_in_zone

    def fetch_drones_in_connection(
            self,
            connection: Connection,
            curren_path: List[Zone]
    ) -> List[Drone]:
        drones_in_connection: List[Drone] = []
        for drone in self.drones:
            if (
                drone.current_position is connection
                and drone.path == curren_path
                and drone.been_in_connection
            ):
                drones_in_connection.append(drone)

        for drone in self.drones:
            if (
                drone.current_position is connection
                and drone.path == curren_path
                and not drone.been_in_connection
            ):
                drones_in_connection.append(drone)

        return drones_in_connection

    def move_drones_in_connection(
            self, connection: Connection,
            to_zone: Zone,
            curren_path: List[Zone]
    ) -> None:
        if to_zone.zone_type != "restricted":
            return None
        if connection.current_size == 0:
            return None
        drones_in_connection: List[Drone] = self.fetch_drones_in_connection(
            connection, curren_path)
        places_available_in_zone: int = self.check_zone_status(to_zone)

        i: int = 0
        for drone in drones_in_connection:
            if i == places_available_in_zone:
                break
            drone.move_to_zone(to_zone)
            self.printer.print_log(
                f"D{drone.id}-{to_zone.name} ",
                to_zone.color
            )
            i += 1

    def moves_drones_in_zone(
            self, current_zone: Zone,
            next_zone: Zone, connection: Connection,
            current_path: List[Zone]
    ) -> None:
        drones_in_zone: List[Drone] = self.fetch_drones_in_zone(
            current_zone, current_path)

        if next_zone.zone_type == "restricted":
            safe_places_in_dst: int = max(
                0,
                next_zone.max_drones -
                next_zone.current_size -
                connection.current_size
            )
            conn_places_available: int = self.check_connection_status(
                current_zone,
                next_zone
            )
            places_available: int = min(
                safe_places_in_dst,
                conn_places_available
            )
            if places_available == 0:
                return None
            else:
                i: int = 0
                for drone in drones_in_zone:
                    if i == places_available:
                        break
                    drone.move_to_connection(connection)
                    print(f"D{drone.id}-{connection.src.name}-"
                          f"{connection.dst.name} ", end="")
                    i += 1
        else:
            zone_places_available: int = self.check_zone_status(next_zone)
            conn_places_available = self.check_connection_status(
                current_zone,
                next_zone
            )
            places_available = min(
                zone_places_available,
                conn_places_available
            )
            if places_available == 0:
                return None
            i = 0
            for drone in drones_in_zone:
                if i == places_available:
                    break
                drone.move_to_zone(next_zone)
                self.printer.print_log(
                    f"D{drone.id}-{next_zone.name} ",
                    next_zone.color
                )
                i += 1

    def start_simulation(self) -> None:
        end_hub_name: str = self.graph.get_end_hub_name()
        end_hub_zone: Zone = self.graph.zones[end_hub_name]
        turns: int = 0
        max_lenght: int = max(len(self.path_1), len(self.path_2))

        while end_hub_zone.current_size != self.nb_drones:
            if turns % 2 == 0:
                first_path, second_path = self.path_1, self.path_2
            else:
                first_path, second_path = self.path_2, self.path_1

            for step in range(max_lenght):
                idx1 = len(first_path) - 1 - step
                if idx1 >= 0 and idx1 < len(first_path) - 1:
                    current = first_path[idx1]
                    next_zone = first_path[idx1 + 1]
                    connection = current.get_connection(next_zone)
                    self.move_drones_in_connection(
                        connection, next_zone, first_path)
                    self.moves_drones_in_zone(
                        current, next_zone, connection, first_path)

                idx2 = len(second_path) - 1 - step
                if idx2 >= 0 and idx2 < len(second_path) - 1:
                    current = second_path[idx2]
                    next_zone = second_path[idx2 + 1]
                    connection = current.get_connection(next_zone)
                    self.move_drones_in_connection(
                        connection, next_zone, second_path)
                    self.moves_drones_in_zone(
                        current, next_zone, connection, second_path)
            turns += 1
            print()
        print(turns)

from Graph import Graph, Zone, Connection
from typing import List


class Drone:
    def __init__(
            self,
            id: int,
            graph: Graph,
            path_1: List[Zone],
            path_2: List[Zone]
    ) -> None:
        self.id: int = id + 1
        self.start_hub_name: str = graph.get_start_hub_name()
        self.current_position: Zone | Connection = (
            graph.zones[self.start_hub_name]
        )
        self.been_in_connection: bool = False
        self.current_position.current_size += 1
        self.path_1 = path_1
        self.path_2 = path_2
        self.assign_path()

    def move_to_zone(self, destination: Zone) -> None:
        self.current_position.current_size -= 1
        self.current_position = destination
        self.current_position.current_size += 1
        self.been_in_connection = False

    def move_to_connection(self, connection: Connection) -> None:
        self.current_position.current_size -= 1
        connection.current_size += 1
        self.been_in_connection = True
        self.current_position = connection

    def assign_path(self) -> None:
        if self.id % 2 != 0:
            self.path = self.path_1
        else:
            self.path = self.path_2

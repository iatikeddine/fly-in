from Graph import Graph, Zone, Connection


class Drone:
    def __init__(self, id: int, graph: Graph):
        self.id: int = id
        self.start_hub_name: str = graph.get_start_hub_name()
        self.current_position: Zone | Connection = (
            graph.zones[self.start_hub_name]
        )
        self.been_in_connection: bool = False
        self.current_position.current_size += 1

    def move_to_zone(self, destination: Zone):
        self.current_position.current_size -= 1
        self.current_position = destination
        self.current_position.current_size += 1
        self.been_in_connection = False

    def move_to_connection(self, connection: Connection) -> None:
        self.current_position.current_size -= 1
        connection.current_size += 1
        self.been_in_connection = True
        self.current_position = connection

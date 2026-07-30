from Graph import Graph, Zone


class Drone:
    def __init__(self, id: int, graph: Graph):
        self.id: int = id
        self.start_hub_name: str = graph.get_end_hub_name()
        self.current_position: Zone = graph.zones[self.start_hub_name]

    def move_to(self, destination: Zone):
        self.current_position.current_size - 1
        self.current_position = destination
        self.current_position += 1

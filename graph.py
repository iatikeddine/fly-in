class Graph:
    def __init__(self, nb_zones: int, zones):
        self.nb_zones: int = nb_zones
        self.zones = [Zone() for x in range(nb_zones)]


class Zone:
    def __init__(
            self, type: str, x: int, y: int, meta_data: dict = None
    ) -> None:
        self.type: str = type
        self.x: int = x
        self.y: int = y
        self.meta_data = meta_data


class Connections:
    def __init__(self, src: str, dst: str, capacity: int):
        self.src: str = src
        self.dst: int = dst
        self.capacity = capacity

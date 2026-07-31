from typing import List, Dict, Union, Tuple


class Connection:
    def __init__(
            self,
            src: "Zone", dst: "Zone", capacity: int
    ) -> None:
        self.src: "Zone" = src
        self.dst: "Zone" = dst
        self.capacity: int = capacity
        self.weight: int = self.get_weight()
        self.current_stat: int = 0

    def get_weight(self) -> int:
        if self.dst.zone_type == "normal":
            return 100
        elif self.dst.zone_type == "priority":
            return 199
        elif self.dst.zone_type == "restricted":
            return 200
        return -1


class Zone:
    def __init__(
            self,
            name: str, x: int, y: int, kind: str,
            zone_type: str, color: Union[str, None],
            max_drones: int
    ) -> None:
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.kind: str = kind
        self.zone_type: str = zone_type
        self.color: Union[None, str] = color
        self.max_drones: int = max_drones
        self.connections: List[Connection] = []
        self.current_size: int = 0

    def __lt__(self, other: "Zone") -> bool:
        return self.name < other.name

    def add_connection(self, dst: "Zone", capacity: int) -> None:
        connection: Connection = Connection(
            self, dst, capacity
        )
        self.connections.append(connection)

    def get_connection(self, next_zone: "Zone") -> Connection:
        for connection in self.connections:
            if connection.dst is next_zone:
                return connection

    def get_neighbors_names(self) -> List[Tuple[int, str]]:
        neighbors_names: List[Tuple[int, str]] = []
        for connection in self.connections:
            if connection.weight != -1:
                name: str = connection.dst.name
                wight: int = connection.weight
                neighbors_names.append((wight, name))
        return neighbors_names


class Graph:
    def __init__(self) -> None:
        self.zones: Dict[str, Zone] = {}

    def add_zones(self, all_zones: List[Zone]) -> None:
        for zone in all_zones:
            self.zones[zone.name] = zone

    @staticmethod
    def create_zones(zones: Dict) -> List[Zone]:
        all_zones: List[Zone] = []
        for name, zone_data in zones.items():
            kind: str = zone_data["type"]
            x: int = zone_data["x"]
            y: int = zone_data["y"]
            zone_type: str = "normal"
            color: Union[None, str] = None
            max_drones: int = 1
            meta_data: Dict = zone_data["meta_data"]
            if meta_data:
                for tag, value in meta_data.items():
                    if tag == "zone":
                        zone_type = value
                    if tag == "color":
                        color = value
                    if tag == "max_drones":
                        max_drones = value
            zone: Zone = Zone(
                name, x, y, kind, zone_type,
                color, max_drones
            )
            all_zones.append(zone)
        return all_zones

    def get_start_hub_name(self) -> str:
        for name, object in self.zones.items():
            if object.kind == "start_hub":
                return name
        return ""

    def get_end_hub_name(self) -> str:
        for name, object in self.zones.items():
            if object.kind == "end_hub":
                return name
        return ""

    def connect_graph(self, connections: Dict[str, Union[None, int]]) -> None:
        for connection, capacity in connections.items():
            src, dst = connection.split('-')
            src_zone: Zone = self.zones[src]
            dst_zone: Zone = self.zones[dst]
            if capacity is not None:
                src_zone.add_connection(dst_zone, capacity)
                dst_zone.add_connection(src_zone, capacity)
            else:
                src_zone.add_connection(dst_zone, 1)
                dst_zone.add_connection(src_zone, 1)

    def get_neighbors_object(
            self,
            neighbors_names: List
    ) -> List | None:
        neighbors_objects: List[Tuple[int, Zone]] = []
        if not neighbors_names:
            return None
        for weight, name in neighbors_names:
            neighbor_object: Zone = self.zones[name]
            neighbors_objects.append((weight, neighbor_object))
        return neighbors_objects

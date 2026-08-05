from typing import List, Dict, Union, Tuple, Any


class Connection:
    """A directed, weighted edge between two zones in the graph.

    The weight is derived from the destination zone's type, so
    routing algorithms can prefer priority zones and penalize
    restricted ones without inspecting zone data directly.
    """

    def __init__(
            self,
            src: "Zone", dst: "Zone", capacity: int
    ) -> None:
        """Initialize a connection from ``src`` to ``dst``.

        :param src: The zone this connection originates from.
        :param dst: The zone this connection leads to.
        :param capacity: The maximum number of drones allowed to
            traverse this link at once.
        """

        self.src: "Zone" = src
        self.dst: "Zone" = dst
        self.capacity: int = capacity
        self.weight: int = self.get_weight()
        self.current_size: int = 0

    def get_weight(self) -> int:
        """Compute this connection's traversal weight from dst's type.

        :return: 100 for a normal destination, 99 for priority (
            slightly cheaper, so it's preferred), 200 for restricted
            (penalized), or -1 if the destination's zone type is
            unrecognized (e.g. ``"blocked"``), signaling the
            connection should not be traversed.
        """

        if self.dst.zone_type == "normal":
            return 100
        elif self.dst.zone_type == "priority":
            return 99
        elif self.dst.zone_type == "restricted":
            return 200
        return -1


class Zone:
    """A single node in the map graph (a hub, start hub, or end hub).

    Holds the zone's static data parsed from the map file (position,
    type, capacity) along with its outgoing Connections and current
    drone occupancy.
    """

    def __init__(
            self,
            name: str, x: int, y: int, kind: str,
            zone_type: str, color: Union[str, None],
            max_drones: int
    ) -> None:
        """Initialize a zone with its parsed attributes.

        :param name: The zone's unique name.
        :param x: The zone's x coordinate.
        :param y: The zone's y coordinate.
        :param kind: "start_hub","end_hub" or "hub".
        :param zone_type: The zone's movement-cost category
            ("normal", "priority", "restricted", or "blocked").
        :param color: The zone's display color, or ``None`` if
            unspecified.
        :param max_drones: The maximum number of drones allowed in
            this zone at once.
        """

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
        """Order zones alphabetically by name.

        Enables zones to be compared

        :param other: The zone to compare against.
        :return: True if this zone's name sorts before other's.
        """

        return self.name < other.name

    def add_connection(self, dst: "Zone", capacity: int) -> None:
        """Create and register an outgoing connection to ``dst``.

        :param dst: The destination zone.
        :param capacity: The maximum number of drones allowed to
            traverse the new connection at once.
        """

        connection: Connection = Connection(
            self, dst, capacity
        )
        self.connections.append(connection)

    def get_connection(self, next_zone: "Zone") -> Connection:
        """Find this zone's outgoing connection to next_zone.

        :param next_zone: The destination zone to look up.
        :return: The Connection whose destination is next_zone.
        """

        target_connection: Connection
        for connection in self.connections:
            if connection.dst is next_zone:
                target_connection = connection
        return target_connection

    def get_neighbors_names(self) -> List[Tuple[int, str]]:
        """List the names and weights of all traversable neighbors.

        Connections whose weight is -1 are excluded.

        :return: A list of (weight, neighbor_name) pairs for each
            traversable outgoing connection.
        """

        neighbors_names: List[Tuple[int, str]] = []
        for connection in self.connections:
            if connection.weight != -1:
                name: str = connection.dst.name
                wight: int = connection.weight
                neighbors_names.append((wight, name))
        return neighbors_names


class Graph:
    """A graph of Zone nodes connected by Connection edges.

    Built in two stages from parsed map data: zones are instantiated
    and registered first, then connections between them are wired up
    using the (name, capacity) pairs produced by the parser.
    """

    def __init__(self) -> None:
        """Initialize an empty graph with no registered zones."""
        self.zones: Dict[str, Zone] = {}

    def add_zones(self, all_zones: List[Zone]) -> None:
        """Register a list of zones in the graph, keyed by name.

        :param all_zones: The Zone objects to add.
        """

        for zone in all_zones:
            self.zones[zone.name] = zone

    @staticmethod
    def create_zones(
        zones: Dict[str, Dict[str, Any]],
        nb_drones: int
    ) -> List[Zone]:
        """Build Zone objects from parsed zone data.

        Reads each zone's type, coordinates, and metadata, applying
        defaults (zone_type="normal", color=None,
        max_drones=1) for any tag not present in the metadata.

        :param zones: A mapping of zone name to its parsed data, as
            produced by ``Parsing.zones`` (each value holding
            "type", "x", "y", and "meta_data").
        :return: The constructed Zone objects, in no particular order.
        """

        all_zones: List[Zone] = []
        for name, zone_data in zones.items():
            kind: str = zone_data["type"]
            x: int = zone_data["x"]
            y: int = zone_data["y"]
            zone_type: str = "normal"
            color: Union[None, str] = None
            if kind == "start_hub" or kind == "end_hub":
                max_drones: int = nb_drones
            max_drones = 1
            meta_data: Dict[str, Any] = zone_data["meta_data"]
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
        """Find the name of the graph's start hub.

        :return: The name of the zone whose ``kind`` is
            ``"start_hub"``.
        """
        start_hub_name: str = ""
        for name, obj in self.zones.items():
            if obj.kind == "start_hub":
                start_hub_name = name

        return start_hub_name

    def get_end_hub_name(self) -> str:
        """Find the name of the graph's end hub.

        :return: The name of the zone whose ``kind`` is ``"end_hub"``.
        """
        end_hub_name: str = ""
        for name, obj in self.zones.items():
            if obj.kind == "end_hub":
                end_hub_name = name

        return end_hub_name

    def connect_graph(self, connections: Dict[str, Union[None, int]]) -> None:
        """Wire up bidirectional connections between registered zones.

        For each "src-dst" key, adds a Connection in both
        directions between the two zones, using the given capacity or
        defaulting to 1 if none was specified.

        :param connections: A mapping of "src-dst" connection keys
            to their link capacity (or None for the default), as
            produced by Parsing.connections.
        """

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
            neighbors_names: List[Tuple[int, str]]
    ) -> Union[List[Tuple[int, Zone]], None]:
        """Resolve neighbor names to their Zone objects.

        :param neighbors_names: A list of (weight, name) pairs,
            as produced by Zone.get_neighbors_names.
        :return: A list of (weight, Zone) pairs, or None if
            neighbors_names is empty.
        """

        neighbors_objects: List[Tuple[int, Zone]] = []
        if not neighbors_names:
            return None
        for weight, name in neighbors_names:
            neighbor_object: Zone = self.zones[name]
            neighbors_objects.append((weight, neighbor_object))
        return neighbors_objects

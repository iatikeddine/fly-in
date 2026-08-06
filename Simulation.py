from typing import List
from Graph import Graph, Zone, Connection
from Drone import Drone
from Printer import ColoredPrint


class Simulation:
    """Runs the turn-by-turn drone simulation over a graph.

    Advances all drones along two candidate paths (processed in
    alternating order each turn to avoid systematically favoring one
    path), respecting zone and connection capacity limits, until
    every drone has reached the end hub.
    """

    def __init__(
            self,
            graph: Graph,
            path_1: List[str],
            path_2: List[str],
            nb_drones: int,
            printer: ColoredPrint
    ) -> None:
        """Initialize the simulation with its graph, paths, and drones.

        :param graph: The graph the simulation runs over.
        :param path_1: Zone names forming the first candidate path,
            from start hub to end hub.
        :param path_2: Zone names forming the second candidate path,
            from start hub to end hub.
        :param nb_drones: The total number of drones to simulate.
        :param printer: The printer used to log colored drone moves.
        """

        self.graph: Graph = graph
        self.path_1: List[Zone] = [graph.zones[name] for name in path_1]
        self.path_2: List[Zone] = [graph.zones[name] for name in path_2]
        self.nb_drones: int = nb_drones
        self.drones: List[Drone] = []
        self.printer: ColoredPrint = printer

    def init_drones(self) -> None:
        """Create and register all drones at the start hub.

        Instantiates ``self.nb_drones`` Drone objects, each assigned
        to ``path_1`` or ``path_2`` depending on its id parity.
        """

        for x in range(self.nb_drones):
            self.drones.append(Drone(
                x, self.graph, self.path_1, self.path_2)
            )

    def check_connection_status(self, current: Zone, next_zone: Zone) -> int:
        """Get the number of free slots on the connection between two zones.

        :param current: The zone the connection originates from.
        :param next_zone: The zone the connection leads to.
        :return: The number of additional drones the connection can
            still hold before reaching its capacity.
        """

        connection: Connection = current.get_connection(next_zone)
        if connection.current_size < connection.capacity:
            return connection.capacity - connection.current_size

        return 0

    def check_zone_status(self, zone: Zone) -> int:
        """Get the number of free slots remaining in a zone.

        The end hub is treated as having unlimited capacity, since it
        is the simulation's final destination for every drone.

        :param zone: The zone to check.
        :return: ``self.nb_drones`` if ``zone`` is the end hub;
            otherwise the number of additional drones the zone can
            still hold before reaching ``max_drones``.
        """

        if zone.kind == "end_hub" or zone.kind == "end_hub":
            return self.nb_drones
        if zone.current_size < zone.max_drones:
            return zone.max_drones - zone.current_size

        return 0

    def fetch_drones_in_zone(
            self,
            zone: Zone,
            current_path: List[Zone]
    ) -> List[Drone]:
        """List all drones currently resting in a zone on a given path.

        :param zone: The zone to search.
        :param current_path: The path a drone must be assigned to in
            order to be included.
        :return: The drones whose current position is ``zone`` and
            whose assigned path is ``current_path``.
        """

        drones_in_zone: List[Drone] = []
        for drone in self.drones:
            if drone.current_position is zone and drone.path == current_path:
                drones_in_zone.append(drone)

        return drones_in_zone

    def fetch_drones_in_connection(
            self,
            connection: Connection,
            curren_path: List[Zone]
    ) -> List[Drone]:
        """List drones currently in transit on a connection, on a given path.

        Drones that have already spent a turn on the connection (
        ``been_in_connection`` is ``True``) are listed first, so they
        are prioritized for the next move over drones that just
        entered the connection this turn.

        :param connection: The connection to search.
        :param curren_path: The path a drone must be assigned to in
            order to be included.
        :return: The matching drones, already-in-transit ones first.
        """

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
        """Advance drones off a connection and into a restricted zone.

        Only applies when ``to_zone`` is a restricted zone; drones
        moving into normal or priority zones are handled directly in
        ``moves_drones_in_zone`` instead. Moves as many waiting
        drones as there is free space in ``to_zone``, logging each
        move.

        :param connection: The connection the drones are currently on.
        :param to_zone: The destination zone.
        :param curren_path: The path whose drones on ``connection``
            should be considered.
        """

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
        """Advance drones out of a zone, toward or into the next zone.

        If ``next_zone`` is restricted, drones are moved onto the
        connecting Connection instead of directly into the zone (
        actual entry into a restricted zone happens later, via
        ``move_drones_in_connection``), and the number moved is
        limited by both the connection's free space and the zone's
        remaining safe capacity net of drones already inbound.
        Otherwise, drones are moved directly into ``next_zone``,
        limited by the zone's and connection's free space.

        :param current_zone: The zone drones are currently resting in.
        :param next_zone: The zone drones are advancing toward.
        :param connection: The connection between ``current_zone`` and
            ``next_zone``.
        :param current_path: The path whose drones in ``current_zone``
            should be considered.
        """

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
                    self.printer.print_log(
                        f"D{drone.id}-{connection.src.name}-"
                        f"{connection.dst.name} ",
                        current_zone.color, next_zone.color)
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
        """Run the simulation until every drone reaches the end hub.

        Each turn, walks both paths from end to start (so drones
        closer to the goal move before the ones behind them, avoiding
        self-blocking), alternating which path is processed first
        every other turn for fairness between the two paths. Prints
        the total number of turns once all drones have arrived.
        """

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
                i1: int = len(first_path) - 1 - step
                if i1 >= 0 and i1 < len(first_path) - 1:
                    current = first_path[i1]
                    next_zone = first_path[i1 + 1]
                    connection = current.get_connection(next_zone)
                    self.move_drones_in_connection(
                        connection, next_zone, first_path)
                    self.moves_drones_in_zone(
                        current, next_zone, connection, first_path)

                if first_path != second_path:
                    i2 = len(second_path) - 1 - step
                    if i2 >= 0 and i2 < len(second_path) - 1:
                        current = second_path[i2]
                        next_zone = second_path[i2 + 1]
                        connection = current.get_connection(next_zone)
                        self.move_drones_in_connection(
                            connection, next_zone, second_path)
                        self.moves_drones_in_zone(
                            current, next_zone, connection, second_path)
            turns += 1
            print()
        print(f"\nTurns to complete simulation: {turns}")

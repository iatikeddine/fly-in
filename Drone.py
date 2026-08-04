from Graph import Graph, Zone, Connection
from typing import List


class Drone:
    """A single drone moving through the graph from the start hub.

    Tracks the drone's current position (a Zone while resting in a
    hub, or a Connection while in transit) and the assigned path it
    should follow to reach the end hub.
    """

    def __init__(
            self,
            id: int,
            graph: Graph,
            path_1: List[Zone],
            path_2: List[Zone]
    ) -> None:
        """Initialize a drone at the graph's start hub.

        Assigns the drone a 1-based id, places it at the start hub
        (incrementing that zone's occupancy), and picks which of the
        two candidate paths it will follow based on parity of its id.

        :param id: The drone's 0-based index; stored internally as
            "id + 1".
        :param graph: The graph the drone will travel through, used
            to look up the start hub.
        :param path_1: The path assigned to odd-numbered drones.
        :param path_2: The path assigned to even-numbered drones.
        """

        self.id: int = id + 1
        self.start_hub_name: str = graph.get_start_hub_name()
        self.current_position: Zone | Connection = (
            graph.zones[self.start_hub_name]
        )
        self.been_in_connection: bool = False
        self.current_position.current_size += 1
        self.path_1: List[Zone] = path_1
        self.path_2: List[Zone] = path_2
        self.path: List[Zone] = []
        self.assign_path()

    def move_to_zone(self, destination: Zone) -> None:
        """Move the drone out of its current position and into a zone.

        Decrements the occupancy of the current position, moves the
        drone into ``destination``, increments its occupancy, and
        clears the "in connection" flag.

        :param destination: The zone the drone is moving into.
        """
        if isinstance(self.current_position, Connection):
            reverse_connection: Connection = destination.get_connection(
                self.current_position.src)
            reverse_connection.current_size -= 1
        self.current_position.current_size -= 1
        self.current_position = destination
        self.current_position.current_size += 1
        self.been_in_connection = False

    def move_to_connection(self, connection: Connection) -> None:
        """Move the drone out of its current zone and onto a connection.

        Decrements the occupancy of the current position, increments
        the connection's occupancy, and marks the drone as in transit.

        :param connection: The connection the drone is moving onto.
        """

        self.current_position.current_size -= 1
        connection.current_size += 1
        self.been_in_connection = True
        self.current_position = connection
        reverse_connection: Connection = connection.dst.get_connection(
            connection.src)
        reverse_connection.current_size += 1

    def assign_path(self) -> None:
        """Assign this drone's path based on the parity of its id.

        Odd ids get ``path_1``; even ids get ``path_2``.
        """

        if self.id % 2 != 0:
            self.path = self.path_1
        else:
            self.path = self.path_2

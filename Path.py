from typing import List, Tuple, Dict, Union
from Graph import Zone, Graph, Connection


class Algorithm:
    """Pathfinding over a Graph using weighted DFS search.

    Wraps a single start hub and its graph, and can produce both the
    shortest path to the end hub and a distinct "second shortest"
    path by iteratively penalizing edges already used.
    """

    def __init__(self, start_hub: Zone, graph: Graph) -> None:
        """Initialize the algorithm with a fixed start hub and graph.

        :param start_hub: The zone to begin searching from.
        :param graph: The graph containing all zones and connections.
        """

        self.start_hub: Zone = start_hub
        self.graph: Graph = graph

    def path_finder(self) -> List[str]:
        """Find the lowest-weight path from the start hub to the end hub.

        Runs a standard search over the graph's connection
        weights, stopping once the queueis empty,
        then reconstructs the path by walking the recorded
        predecessor trace back from the end hub to the start hub.

        :return: The list of zone names forming the path,
            ordered from start hub to end hub inclusive.
        """

        queue: List[Tuple[int, Zone]] = [(0, self.start_hub)]
        paths_trace: Dict[str, str] = {}
        cost_so_far: Dict[str, int] = {self.start_hub.name: 0}
        while queue:
            current_weight, current_zone = queue.pop()
            neighbors_names: List[Tuple[int, str]] = (
                current_zone.get_neighbors_names())
            neighbors:  Union[List[Tuple[int, Zone]], None] = (
                self.graph.get_neighbors_object(neighbors_names))
            if not neighbors:
                continue
            for weight, neighbor in neighbors:
                weight += current_weight
                n_name: str = neighbor.name
                if n_name not in cost_so_far or weight < cost_so_far[n_name]:
                    cost_so_far[neighbor.name] = weight
                    queue.append((weight, neighbor))
                    paths_trace[neighbor.name] = current_zone.name

        path: List[str] = []
        currenst_step: str = self.graph.get_end_hub_name()
        if currenst_step not in paths_trace:
            raise ValueError(
                "Error: end hub is not connected to the Graph\n"
                "end_hub line"
            )
        target: str = self.graph.get_start_hub_name()
        while currenst_step != target:
            path.append(currenst_step)
            currenst_step = paths_trace[currenst_step]
        path.append(target)
        path.reverse()
        return path

    def second_path(self, path: List[str]) -> List[str]:
        """Find a path distinct from "path" by penalizing its edges.

        Repeatedly increments the weight of every connection used by
        "path" by 1 and reruns path_finder, until the result differs
        from "path" or the retry limit (100 iterations) is reached.

        :param path: The reference path (e.g. the current shortest
            path) to diverge away from.
        :return: A new path distinct from "path" if
            one was found within the retry limit; otherwise the last
            (still-identical) result.
        """

        second_shortest: List[str] = path
        limit: int = 0
        while second_shortest == path:
            if limit >= 100:
                break
            for x in range(len(path) - 1):
                src_name: str = path[x]
                dst_name: str = path[x + 1]

                src_zone: Zone = self.graph.zones[src_name]
                dst_zone: Zone = self.graph.zones[dst_name]

                conn: Connection = src_zone.get_connection(dst_zone)
                rev_conn: Connection = dst_zone.get_connection(src_zone)
                conn.weight += 1
                rev_conn.weight += 1
            second_shortest = self.path_finder()
            limit += 1

        return second_shortest

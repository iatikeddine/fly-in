from typing import List, Tuple, Dict
from Graph import Zone, Graph, Connection
import heapq


class Algorithm:
    def __init__(self, start_hub: Zone, graph: Graph):
        self.start_hub: Zone = start_hub
        self.graph: Graph = graph

    def Dijkstra(self) -> List[str]:
        queue: List[Tuple[int, Zone]] = [(0, self.start_hub)]
        heapq.heapify(queue)
        paths_trace: Dict[str, str] = {}
        cost_so_far: Dict[str, int] = {self.start_hub.name: 0}
        while queue:
            current_weight, current_zone = heapq.heappop(queue)
            neighbors_names: List[Tuple[int, str]] = (
                current_zone.get_neighbors_names())
            neighbors: List | None = (
                self.graph.get_neighbors_object(neighbors_names))
            if not neighbors:
                continue
            if current_zone.kind == "end_hub":
                break
            for weight, neighbor in neighbors:
                weight += current_weight
                n_name: str = neighbor.name
                if n_name not in cost_so_far or weight < cost_so_far[n_name]:
                    cost_so_far[neighbor.name] = weight
                    heapq.heappush(queue, (weight, neighbor))
                    paths_trace[neighbor.name] = current_zone.name

        path: List[str] = []
        currenst_step: str = self.graph.get_end_hub_name()
        target: str = self.graph.get_start_hub_name()
        while currenst_step != target:
            path.append(currenst_step)
            currenst_step = paths_trace[currenst_step]
        path.append(target)
        path.reverse()
        return path

    def second_shortest_path(self, path: List[str]) -> List[str]:
        second_shortest: List[str] = path
        while second_shortest == path:
            for x in range(len(path) - 1):
                src_name: str = path[x]
                dst_name: str = path[x + 1]

                src_zone: Zone = self.graph.zones[src_name]
                dst_zone: Zone = self.graph.zones[dst_name]

                conn: Connection = src_zone.get_connection(dst_zone)
                conn.weight += 1
            second_shortest = self.Dijkstra()
        return second_shortest

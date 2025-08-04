import sys
from MinHeap import MinHeap

infinity = sys.maxsize


class Dijkstra:
    def __init__(self):
        self.graph = {}

    def add_edge(self, u, v, weight):
        self.graph.setdefault(u,[]).append((v, weight))

    def shortest_path(self, start, target):
        dist = {}
        previous = {}
        pq = MinHeap()
        visited_count = 0

        for v in self.graph:
            if v == start:
                dist[v] = 0
                pq.insert(v, 0)
            else:
                dist[v] = infinity
                pq.insert(v, infinity)
            previous[v] = None

        while not pq.empty():
            u, du = pq.extract_min()
            visited_count += 1
            if u == target:
                break
            # if du is infinity, the remaining nodes are unreachable
            if du == infinity:
                break

            for v, w in self.graph.get(u, []):
                if pq.contains(v) and dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    previous[v] = u
                    pq.decrease_key(v, dist[v])
        #write the path
        path = []
        u  = target
        if (u in previous or u == start):
            while u != start:
                path.append(u)
                u = previous[u]

            path.append(start)
            path.reverse()
        return path, visited_count

    #for testing
    def print_path(self, target, previous):
        # recursive printing
        if previous[target] is None:
            print(target, end='')
        else:
            self.print_path(previous[target], previous)
            print(f" -> {target}", end='')



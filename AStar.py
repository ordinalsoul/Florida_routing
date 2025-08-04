import math
from MinHeap import MinHeap

infinity = float('inf')

def astar(adj, source, target, coords):

    # quick checks
    if source == target:
        return [source], 0
    if source not in coords or target not in coords:
        return [], 0

    def heuristic(u, v):
        x1, y1 = coords[u]
        x2, y2 = coords[v]
        return math.hypot(x1 - x2, y1 - y2)


    g_score = {u: infinity for u in adj}
    parent  = {u: None   for u in adj}
    g_score[source] = 0.0

    open_set = MinHeap()
    open_set.insert(source, heuristic(source, target))

    closed = set()
    expanded = 0

    while not open_set.empty():
        u, _ = open_set.extract_min()
        if u in closed:
            continue
        closed.add(u)
        expanded += 1

        if u == target:
            break

        for v, w in adj[u]:
            if v not in coords:
                continue
            tentative = g_score[u] + w
            if tentative < g_score.get(v, infinity):
                g_score[v] = tentative
                parent[v]  = u
                f = tentative + heuristic(v, target)
                if open_set.contains(v):
                    open_set.decrease_key(v, f)
                else:
                    open_set.insert(v, f)

    # writing the path
    path = []
    if g_score.get(target, infinity) < infinity:
        u = target
        while u is not None:
            path.append(u)
            u = parent[u]
        path.reverse()

    return path, expanded
import os
import time
import osmnx as ox
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import pickle
import networkx as nx
from collections import defaultdict
from ShortestPath import Dijkstra
from AStar import astar

# Path to cache the downloaded graph using pickle
GPICKLE_PATH = "Florida.pkl"


def load_or_download_graph():
    """
    Load the driving graph from a pickle cache if available, otherwise download via OSMnx,
    and save via pickle for future runs.
    """
    if os.path.exists(GPICKLE_PATH):
        print("Loading graph from pickle cache…")
        with open(GPICKLE_PATH, 'rb') as f:
            G = pickle.load(f)
    else:
        print("Downloading graph…")
        G = ox.graph_from_place(
            #write the name of city or state you want here
            "Florida, USA",
            network_type="drive", simplify=True
        )
        G = ox.project_graph(G)
        print("Saving graph to pickle cache…")
        with open(GPICKLE_PATH, 'wb') as f:
            pickle.dump(G, f, protocol=pickle.HIGHEST_PROTOCOL)
    return G


def build_graph_data(G):
    """
    Convert the OSMnx graph into:
      - adj: node -> list of (neighbor, length)
      - coords: node -> (x, y) projected coordinates
    """
    adj = defaultdict(list)
    coords = {}
    for u, v, data in G.edges(data=True):
        length = data.get("length", 1.0)
        adj[u].append((v, length))
        adj[v].append((u, length))
    for n, data in G.nodes(data=True):
        coords[n] = (data.get('x'), data.get('y'))
    return adj, coords


def dijkstra(adj, source, target):
    d = Dijkstra()
    for u, neighbors in adj.items():
        for v, w in neighbors:
            d.add_edge(u,v,w)

    path, visited_count = d.shortest_path(source, target)
    return path, visited_count


def nearest_node(point, coords):
    x0, y0 = point
    return min(coords.keys(), key=lambda n: (coords[n][0]-x0)**2 + (coords[n][1]-y0)**2)


def main():
    G = load_or_download_graph()
    G = G.to_undirected()
    adj, coords = build_graph_data(G)
    total_nodes = len(coords)

    # Set up plot and buttons
    fig, ax = plt.subplots(figsize=(8, 8))
    plt.subplots_adjust(bottom=0.3)
    xs, ys = zip(*coords.values())
    ax.scatter(xs, ys, s=1, color="#888", alpha=0.6)
    ax.set_title(f"Nodes: {total_nodes} — Click SOURCE then TARGET")
    original_xlim = ax.get_xlim()
    original_ylim = ax.get_ylim()

    clicks = []
    markers = []
    paths = []
    text_annotation = None
    active = True

    # Buttons: Reset, Zoom In, Zoom Out, Pan Left/Right/Up/Down
    axreset    = plt.axes([0.05, 0.02, 0.1, 0.05])
    axzoomin   = plt.axes([0.16, 0.02, 0.1, 0.05])
    axzoomout  = plt.axes([0.27, 0.02, 0.1, 0.05])
    axpanleft  = plt.axes([0.5, 0.02, 0.05, 0.05])
    axpanright = plt.axes([0.56, 0.02, 0.05, 0.05])
    axpanup    = plt.axes([0.62, 0.02, 0.05, 0.05])
    axpandown  = plt.axes([0.68, 0.02, 0.05, 0.05])

    breset    = Button(axreset,    'Reset')
    bzi       = Button(axzoomin,   '+')
    bzo       = Button(axzoomout,  '-')
    bleft     = Button(axpanleft,  '<')
    bright    = Button(axpanright, '>')
    bup       = Button(axpanup,    '^')
    bdown     = Button(axpandown,  'v')

    def zoom(factor):
        x0, x1 = ax.get_xlim()
        y0, y1 = ax.get_ylim()
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        dx, dy = (x1 - x0) * factor / 2, (y1 - y0) * factor / 2
        ax.set_xlim(cx - dx, cx + dx)
        ax.set_ylim(cy - dy, cy + dy)
        fig.canvas.draw()

    def pan(dx_frac, dy_frac):
        x0, x1 = ax.get_xlim()
        y0, y1 = ax.get_ylim()
        dx, dy = (x1 - x0) * dx_frac, (y1 - y0) * dy_frac
        ax.set_xlim(x0 + dx, x1 + dx)
        ax.set_ylim(y0 + dy, y1 + dy)
        fig.canvas.draw()

    def reset(event):
        nonlocal clicks, markers, paths, text_annotation, active
        clicks.clear()
        for m in markers:
            try: m.remove()
            except: pass
        markers.clear()
        for p in paths:
            try: p.remove()
            except: pass
        paths.clear()
        if text_annotation:
            try: text_annotation.remove()
            except: pass
            text_annotation = None
        ax.set_title(f"Nodes: {total_nodes} — Click SOURCE then TARGET")
        ax.set_xlim(original_xlim)
        ax.set_ylim(original_ylim)
        fig.canvas.draw()
        active = True

    # Bind button callbacks
    breset.on_clicked(reset)
    bzi.on_clicked(lambda e: zoom(0.5))
    bzo.on_clicked(lambda e: zoom(2.0))
    bleft.on_clicked(lambda e: pan(-0.2, 0))
    bright.on_clicked(lambda e: pan(0.2, 0))
    bup.on_clicked(lambda e: pan(0, 0.2))
    bdown.on_clicked(lambda e: pan(0, -0.2))

    def on_click(event):
        nonlocal text_annotation, active
        if not event.inaxes or not active:
            return
        x, y = event.xdata, event.ydata
        if x < original_xlim[0] or x > original_xlim[1] or y < original_ylim[0] or y > original_ylim[1]:
            return
        marker, = ax.plot(x, y, 'ro')
        markers.append(marker)
        fig.canvas.draw()
        clicks.append((x, y))
        if len(clicks) == 2:
            active = False
            src = nearest_node(clicks[0], coords)
            dst = nearest_node(clicks[1], coords)

            t0 = time.time()
            d_path, d_vis = dijkstra(adj, src, dst)
            t1 = time.time()
            d_time = t1 - t0
            t2 = time.time()
            a_path, a_vis = astar(adj, src, dst, coords)
            t3 = time.time()
            a_time = t3 - t2

            metrics = (
                f"Dijkstra: {d_time:.2f}s, visited {d_vis} nodes\n"
                f"A*:        {a_time:.2f}s, visited {a_vis} nodes"
            )
            text_annotation = ax.text(
                0.02, 0.98, metrics,
                transform=ax.transAxes,
                verticalalignment='top',
                bbox=dict(facecolor='white', alpha=0.8)
            )

            px = [coords[n][0] for n in a_path]
            py = [coords[n][1] for n in a_path]
            ln, = ax.plot(px, py, color='red', linewidth=2)
            paths.append(ln)
            fig.canvas.draw()

    fig.canvas.mpl_connect('button_press_event', on_click)
    plt.show()

if __name__ == "__main__":
    main()

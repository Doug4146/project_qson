import matplotlib.cm as cm
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from src.node import Node


def visualize_clusters(
    nodes: list[Node], save_path: str = "output_images\\clusters.png"
):
    """Plot all nodes colored by cluster, labeled by name."""

    cluster_ids = [n.attributes.get("cluster", 0) for n in nodes]
    unique_clusters = sorted(set(cluster_ids))
    colors = cm.tab10(np.linspace(0, 1, len(unique_clusters)))
    color_map = {c: colors[i] for i, c in enumerate(unique_clusters)}

    plt.figure(figsize=(12, 8))
    for node in nodes:
        c = node.attributes.get("cluster", 0)
        plt.scatter(node.lon, node.lat, color=color_map[c], s=80, zorder=3)
        plt.annotate(
            node.name,
            (node.lon, node.lat),
            fontsize=6,
            textcoords="offset points",
            xytext=(4, 4),
        )

    plt.title("Node Clusters")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    print("[viz] Cluster plot saved to clusters.png")
    plt.show()


def visualize_graph(
    G: nx.Graph,
    path: list[str] = None,
    save_path: str = "output_images\\hyperloop_network.png",
):
    """
    Plot the graph using lat/lon as coordinates and save to disk.
    Optionally plot a path.
    """
    pos = {nid: (d["lon"], d["lat"]) for nid, d in G.nodes(data=True)}
    labels = {nid: d.get("name", nid) for nid, d in G.nodes(data=True)}

    plt.figure(figsize=(12, 8))
    nx.draw(
        G,
        pos,
        labels=labels,
        node_size=100,
        node_color="steelblue",
        font_size=7,
        edge_color="gray",
        width=0.8,
    )

    # draw route on top if provided
    if path and len(path) > 1:
        path_edges = list(zip(path[:-1], path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color="red", width=3)
        nx.draw_networkx_nodes(G, pos, nodelist=path, node_color="red", node_size=150)

    plt.title("Hyperloop Network")
    # plt.tight_layout()
    plt.layout_engine = "constrained"
    plt.savefig(save_path, dpi=150)
    print(f"[viz] Saved to {save_path}")
    plt.show()

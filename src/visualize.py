import matplotlib.cm as cm
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from src.node import Node


def visualize_clusters(nodes: list[Node], filename: str):
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
    plt.savefig(filename, dpi=150)
    print("[viz] Cluster plot saved to clusters.png")
    plt.show()


def visualize(G: nx.Graph, save_path: str = "network_graph.png"):
    """Plot the graph using lat/lon as coordinates and save to disk."""
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
    plt.title("Hyperloop Network")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    print(f"[viz] Saved to {save_path}")
    plt.show()

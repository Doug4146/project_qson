import matplotlib.pyplot as plt
import networkx as nx


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

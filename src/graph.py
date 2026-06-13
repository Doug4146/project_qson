import networkx as nx
from geopy.distance import geodesic

from src.node import Node


def build_graph(nodes: list[Node]) -> nx.Graph:
    """
    Build a NetworkX graph from nodes.
    Edges are formed using a minimum spanning tree.
    Weight = geodesic distance for now; Phase 2 replaces this with a real cost function.
    """
    G = nx.Graph()

    for node in nodes:
        G.add_node(
            node.id, name=node.name, lat=node.lat, lon=node.lon, **node.attributes
        )

    # first build a complete graph with all distances
    for i, a in enumerate(nodes):
        for b in nodes[i + 1 :]:
            dist = geodesic((a.lat, a.lon), (b.lat, b.lon)).km
            G.add_edge(a.id, b.id, weight=dist, distance_km=dist)

    # then reduce to minimum spanning tree — nearest neighbor connections only
    G = nx.minimum_spanning_tree(G)

    print(f"[graph] {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


def find_node_by_name(G: nx.Graph, name: str) -> str | None:
    """Returns node ID matching the given name, or None if not found."""
    for node_id, data in G.nodes(data=True):
        if data.get("name", "").lower() == name.lower():
            return node_id
    print(f"[graph] Node '{name}' not found in graph")
    return None


def find_path(G: nx.Graph, source_id: str, target_id: str) -> list[str]:
    """A* between two node IDs. Returns list of node IDs or empty list."""

    def heuristic(u, v):
        u_data, v_data = G.nodes[u], G.nodes[v]
        return geodesic(
            (u_data["lat"], u_data["lon"]), (v_data["lat"], v_data["lon"])
        ).km

    try:
        return nx.astar_path(
            G, source_id, target_id, heuristic=heuristic, weight="weight"
        )
    except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
        print(f"[graph] {e}")
        return []

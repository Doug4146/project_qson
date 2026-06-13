import networkx as nx
from geopy.distance import geodesic

from src.node import Node
from src.config import DIRECTED_GRAPH, EDGE_PROXIMITY_THRESHOLD_KM


def build_graph(nodes: list[Node]) -> nx.Graph:
    """
    Build a NetworkX graph from nodes.
    Edges connect any two nodes within EDGE_PROXIMITY_THRESHOLD_KM.
    Weight = geodesic distance for now; Phase 2 replaces this with a real cost function.
    """
    G = nx.DiGraph() if DIRECTED_GRAPH else nx.Graph()

    for node in nodes:
        G.add_node(
            node.id, name=node.name, lat=node.lat, lon=node.lon, **node.attributes
        )

    for i, a in enumerate(nodes):
        for b in nodes[i + 1 :]:
            dist = geodesic((a.lat, a.lon), (b.lat, b.lon)).km
            if dist <= EDGE_PROXIMITY_THRESHOLD_KM:
                G.add_edge(a.id, b.id, weight=dist, distance_km=dist)
                # TODO Phase 2: weight = compute_edge_cost(a, b, dist)

    print(f"[graph] {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


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


# TODO Phase 3: schedule_traffic(G, demands)

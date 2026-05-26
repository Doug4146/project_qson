import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
import geopandas as gpd
from shapely.geometry import box
from geopy.distance import geodesic
from dataclasses import dataclass, field
from typing import Any

# Temporary configuration
BOUNDING_BOX = {
    "min_lat": 41.0, "max_lat": 41.5,
    "min_lon": -88.5, "max_lon": -88.0,
}

EDGE_PROXIMITY_THRESHOLD_KM = 150  # max distance between nodes to create an edge
MIN_POPULATION = None  # set to an int (e.g. 50000) to filter small places
DIRECTED_GRAPH = False


@dataclass
class Node:
    """
    Represents a single hyperloop network node
    """
    id: str  # Unique identifier
    name: str  # Readable identifier
    lat: float  # Latitude
    lon: float  # Longitude
    attributes: dict[str, Any] = field(
        default_factory=dict)  # Will be expanded to hold more properties (economic, geospatial, etc.)

    def __repr__(self):
        return f"Node({self.id}, '{self.name}', lat={self.lat}, lon={self.lon})"


def fetch_nodes_from_osm(bbox: dict) -> list[Node]:
    """Pull populated places from OSM within the bounding box, return as Nodes."""
    print(f"[fetch] Querying OSM within bbox: {bbox}")

    region = box(bbox["min_lon"], bbox["min_lat"], bbox["max_lon"], bbox["max_lat"])
    tags = {"place": ["city", "town"]}

    try:
        gdf = ox.features_from_polygon(region, tags=tags)
    except Exception as e:
        print(f"[fetch] OSM query failed: {e}")
        return []

    nodes = []
    for idx, row in gdf.iterrows():
        geom = row.geometry
        if geom is None:
            continue

        centroid = geom.centroid
        name = row.get("name", "Unknown")
        population = row.get("population", None)

        # filter out small places if population data is available
        if population is not None:
            try:
                if int(population) < MIN_POPULATION:
                    continue
            except (ValueError, TypeError):
                pass

        nodes.append(Node(
            id=str(idx),
            name=name,
            lat=centroid.y,
            lon=centroid.x,
            attributes={"population": population}
            # Later: also fetch elevation, geology_viability, freight_demand, etc.
        ))

    print(f"[fetch] {len(nodes)} candidate nodes found")
    return nodes


# Later: fetch_elevation_data(nodes), fetch_geology_data(nodes)
# Later: fetch_freight_demand(nodes)

def build_graph(nodes: list[Node]) -> nx.Graph:
    """Build a NetworkX graph from nodes. Edges = proximity, weight = distance."""
    G = nx.DiGraph() if DIRECTED_GRAPH else nx.Graph()

    for node in nodes:
        G.add_node(node.id, name=node.name, lat=node.lat, lon=node.lon, **node.attributes)

    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            dist = geodesic((a.lat, a.lon), (b.lat, b.lon)).km
            if dist <= EDGE_PROXIMITY_THRESHOLD_KM:
                G.add_edge(a.id, b.id, weight=dist, distance_km=dist)
                # Phase 2: replace weight with a real cost function (terrain, geology, etc.)

    print(f"[graph] {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


def find_path(G: nx.Graph, source_id: str, target_id: str) -> list[str]:
    """A* between two node IDs. Returns list of node IDs or empty list."""

    def heuristic(u, v):
        u_data, v_data = G.nodes[u], G.nodes[v]
        return geodesic((u_data["lat"], u_data["lon"]), (v_data["lat"], v_data["lon"])).km

    try:
        return nx.astar_path(G, source_id, target_id, heuristic=heuristic, weight="weight")
    except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
        print(f"[routing] {e}")
        return []


def visualize(G: nx.Graph):
    """Creates a vizualization of the graph"""
    pos = {nid: (d["lon"], d["lat"]) for nid, d in G.nodes(data=True)}
    labels = {nid: d.get("name", nid) for nid, d in G.nodes(data=True)}

    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, labels=labels, node_size=100, node_color="steelblue",
            font_size=7, edge_color="gray", width=0.8)
    plt.title("Hyperloop Network — Phase 1")
    plt.tight_layout()
    plt.savefig("network_graph.png", dpi=150)
    print("[viz] Saved to network_graph.png")
    plt.show()


def main():
    nodes = fetch_nodes_from_osm(BOUNDING_BOX)
    if not nodes:
        print("No nodes returned. Check bounding box or OSM query.")
        return

    G = build_graph(nodes)
    if G.number_of_edges() == 0:
        print("No edges. Try increasing EDGE_PROXIMITY_THRESHOLD_KM.")
        return

    # sanity check: find a path between first and last node
    ids = list(G.nodes)
    if len(ids) >= 2:
        path = find_path(G, ids[0], ids[-1])
        if path:
            names = [G.nodes[n].get("name", n) for n in path]
            print(f"[main] Path: {' → '.join(names)}")

    visualize(G)


if __name__ == "__main__":
    main()

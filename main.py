from src.config import BOUNDING_BOX
from src.data import fetch_nodes
from src.graph import build_graph, find_path
from src.visualize import visualize


def main():
    nodes = fetch_nodes(BOUNDING_BOX)
    if not nodes:
        print("No nodes returned. Check BOUNDING_BOX or OSM query.")
        return

    G = build_graph(nodes)
    if G.number_of_edges() == 0:
        print("No edges. Try increasing EDGE_PROXIMITY_THRESHOLD_KM in config.py")
        return

    # sanity check: path between first and last node
    ids = list(G.nodes)
    if len(ids) >= 2:
        path = find_path(G, ids[0], ids[-1])
        if path:
            names = [G.nodes[n].get("name", n) for n in path]
            print(f"[main] Path: {' → '.join(names)}")

    visualize(G)


if __name__ == "__main__":
    main()

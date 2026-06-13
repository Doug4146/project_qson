from src.config import BOUNDING_BOX
from src.data import fetch_nodes, enrich_nodes
from src.graph import build_graph, find_path
from src.visualize import visualize


def main():
    # Get nodes
    nodes = fetch_nodes(BOUNDING_BOX)
    if not nodes:
        print("No nodes returned. Check BOUNDING_BOX or OSM query.")
        return

    G = build_graph(nodes)
    if G.number_of_edges() == 0:
        print("No edges. Try increasing EDGE_PROXIMITY_THRESHOLD_KM in config.py")
        return

    # Add data attributes to nodes
    nodes = enrich_nodes(nodes, BOUNDING_BOX)

    # sanity check: path between first and last node
    ids = list(G.nodes)
    if len(ids) >= 2:
        path = find_path(G, ids[0], ids[-1])
        if path:
            names = [G.nodes[n].get("name", n) for n in path]
            print(f"[main] Path: {' → '.join(names)}")

    for i in range(len(nodes)):
        sample = nodes[i]
        print(f"\n[main] Sample node attributes for '{sample.name}':")
        for (
            k,
            v,
        ) in sample.attributes.items():
            print(f"  {k}: {v}")

    visualize(G)


if __name__ == "__main__":
    main()

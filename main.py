from src.config import BOUNDING_BOX, WEIGHT_PROFILES, ACTIVE_PROFILE, TOP_N_NODES
from src.data import fetch_nodes, enrich_nodes
from src.scoring import normalize_nodes, score_nodes, select_nodes
from src.graph import build_graph, find_path
from src.visualize import visualize, visualize_clusters


def main():
    # fetch and enrich nodes
    nodes = fetch_nodes(BOUNDING_BOX)
    if not nodes:
        print("No nodes returned. Check BOUNDING_BOX or OSM query.")
        return
    nodes = enrich_nodes(nodes, BOUNDING_BOX)

    # Add data attributes to nodes and perform scoring
    nodes = normalize_nodes(nodes)
    nodes = score_nodes(nodes, WEIGHT_PROFILES[ACTIVE_PROFILE])
    select_nodes(nodes, TOP_N_NODES)

    visualize_clusters(nodes, "clusters.png")

    nodes = select_nodes(nodes, TOP_N_NODES)

    visualize_clusters(nodes, "selected_nodes.png")


    # visualize 

    # G = build_graph(nodes)
    # if G.number_of_edges() == 0:
    #     print("No edges. Try increasing EDGE_PROXIMITY_THRESHOLD_KM in config.py")
    #     return

    # # sanity check: path between first and last node
    # ids = list(G.nodes)
    # if len(ids) >= 2:
    #     path = find_path(G, ids[0], ids[-1])
    #     if path:
    #         names = [G.nodes[n].get("name", n) for n in path]
    #         print(f"[main] Path: {' → '.join(names)}")

    # for i in range(len(nodes)):
    #     sample = nodes[i]
    #     print(f"\n[main] Sample node attributes for '{sample.name}':")
    #     for (
    #         k,
    #         v,
    #     ) in sample.attributes.items():
    #         print(f"  {k}: {v}")

    # visualize(G)


if __name__ == "__main__":
    main()

from src.config import (
    BOUNDING_BOX,
    WEIGHT_PROFILES,
    ACTIVE_PROFILE,
    TOP_N_NODES,
    ROUTE_START,
    ROUTE_END,
)
from src.data import fetch_nodes, enrich_nodes
from src.scoring import normalize_nodes, score_nodes, select_nodes
from src.graph import build_graph, find_path, find_node_by_name
from src.visualize import visualize_graph, visualize_clusters


def main():
    """
    Main executing script
    """

    print("=" * 50)
    print("HYPERLOOP NETWORK GENERATOR")
    print("=" * 50)

    # --- Step 1: Fetch nodes ---
    print("\n[1/5] Fetching nodes from OSM...")
    all_nodes = fetch_nodes(BOUNDING_BOX)
    if not all_nodes:
        print("No nodes returned. Check BOUNDING_BOX or OSM query.")
        return
    print(f"      {len(all_nodes)} nodes fetched")

    # --- Step 2: Enrich nodes with attributes ---
    print("\n[2/5] Enriching nodes with geographic and economic data...")
    all_nodes = enrich_nodes(all_nodes, BOUNDING_BOX)

    # --- Step 3: Score nodes ---
    print(f"\n[3/5] Scoring nodes using '{ACTIVE_PROFILE}' profile...")
    nodes = normalize_nodes(all_nodes)
    nodes = score_nodes(nodes, WEIGHT_PROFILES[ACTIVE_PROFILE])

    # --- Step 4: Select best nodes via K-means ---
    print(f"\n[4/5] Selecting top {TOP_N_NODES} nodes via K-means clustering...")
    selected_nodes = select_nodes(all_nodes, TOP_N_NODES)
    visualize_clusters(all_nodes)

    # --- Step 5: Build and visualize graph ---
    print("\n[5/5] Building network graph and finding optimal route...")
    G = build_graph(selected_nodes)
    if G.number_of_edges() == 0:
        print(
            "      No edges formed. Try increasing EDGE_PROXIMITY_THRESHOLD_KM in config.py"
        )
        return
    visualize_graph(G, save_path="output_images\\hyperloop_network.png")

    source = find_node_by_name(G, ROUTE_START)
    target = find_node_by_name(G, ROUTE_END)
    path = []
    if source and target:
        path = find_path(G, source, target)
        if path:
            names = [G.nodes[n].get("name", n) for n in path]
            print(f"      Route: {' → '.join(names)}")
    visualize_graph(G, path=path, save_path="output_images\\optimal_path.png")

    print("\nDone.")


if __name__ == "__main__":
    main()

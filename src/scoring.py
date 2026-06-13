import numpy as np
from sklearn.cluster import KMeans

from src.node import Node


# list of Node attributes
ATTRIBUTES = [
    "elevation_variance",
    "transport_access_count",
    "dist_to_port_km",
    "dist_to_major_city_km",
]


# Attributes where LOWER is better — these get inverted during scoring
INVERT = ["elevation_variance", "dist_to_port_km", "dist_to_major_city_km"]


def normalize_nodes(nodes: list[Node]) -> list[Node]:
    """
    Normalizes each attribute across nodes to a 0-1 scale for easier scoring.
    Stores result in node.attributes as "<attr>_norm".
    Skips nodes where the attribute is None.
    """

    for attr in ATTRIBUTES:
        # collect all non-None values for this attribute
        values = [
            n.attributes[attr] for n in nodes if n.attributes.get(attr) is not None
        ]

        if not values:
            print(f"[scoring] No values for {attr}, skipping normalization")
            for n in nodes:
                n.attributes[f"{attr}_norm"] = None
            continue

        lo, hi = min(values), max(values)

        for node in nodes:
            raw = node.attributes.get(attr)
            if raw is None or lo == hi:
                node.attributes[f"{attr}_norm"] = None
                continue
            node.attributes[f"{attr}_norm"] = (raw - lo) / (hi - lo)

    print("[scoring] Normalization complete")
    return nodes


def score_nodes(nodes: list[Node], weights: dict) -> list[Node]:
    """
    Applies weights to normalized attributes to produce a single node_score.
    Attributes in INVERT are flipped (1 - norm) so lower raw = higher score.
    Nodes with missing normalized values get a score of 0 for that attribute.
    """
    for node in nodes:
        score = 0.0
        for attr, weight in weights.items():
            norm = node.attributes.get(f"{attr}_norm")
            if norm is None:
                continue
            # invert where lower raw value = better
            if attr in INVERT:
                norm = 1 - norm
            score += weight * norm
        node.attributes["node_score"] = round(score, 4)
        print(f"[scoring] {node.name}: {node.attributes['node_score']}")

    print("[scoring] Scoring complete")
    return nodes


def select_nodes(nodes: list[Node], k: int) -> list[Node]:
    """
    Clusters nodes geographically using K-means, then selects the
    highest scoring node from each cluster.
    Returns k nodes spread across the bbox.
    """
    coords = np.array([[n.lat, n.lon] for n in nodes])

    # run the K-Means algorithm to geographically cluster the nodes
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(coords)

    # attach cluster label to each node for debugging
    for node, label in zip(nodes, labels):
        node.attributes["cluster"] = int(label)

    # print cluster summary
    from collections import defaultdict

    cluster_groups = defaultdict(list)
    for node in nodes:
        cluster_groups[node.attributes["cluster"]].append(node.name)
    for cluster_id, names in sorted(cluster_groups.items()):
        print(f"[scoring] Cluster {cluster_id}: {', '.join(names)}")

    # pick highest scoring node from each cluster
    selected = []
    for cluster_id in range(k):
        cluster_nodes = [n for n in nodes if n.attributes["cluster"] == cluster_id]
        if not cluster_nodes:
            print(f"[scoring] Cluster {cluster_id} is empty, skipping")
            continue
        best = max(cluster_nodes, key=lambda n: n.attributes.get("node_score", 0))
        selected.append(best)
        print(
            f"[scoring] Cluster {cluster_id} winner: {best.name} (score: {best.attributes['node_score']})"
        )

    print(f"[scoring] Selected {len(selected)} nodes")
    return selected

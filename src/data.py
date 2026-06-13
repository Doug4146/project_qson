import math

import osmnx as ox
import requests
from geopy.distance import geodesic
from shapely.geometry import box

from src.node import Node

# Cache OSM queries to improve performance
ox.settings.use_cache = True


# -----------------------------------------------------------------------------
# OSM FETCH
# -----------------------------------------------------------------------------


def fetch_nodes(bbox: dict) -> list[Node]:
    """
    Fetch candidate nodes from OSM for the given bounding box.
    Phase 2: replace or supplement this with raster-based discovery
    (population density grids, elevation data, etc.)
    """
    print(f"[data] Querying OSM within bbox: {bbox}")

    region = box(bbox["min_lon"], bbox["min_lat"], bbox["max_lon"], bbox["max_lat"])
    tags = {"place": ["city", "town", "village", "hamlet"]}

    try:
        gdf = ox.features_from_polygon(region, tags=tags)
    except Exception as e:
        print(f"[data] OSM query failed: {e}")
        return []

    nodes = []
    for idx, row in gdf.iterrows():
        geom = row.geometry
        if geom is None:
            continue

        centroid = geom.centroid
        name = row.get("name", "Unknown")
        population = row.get("population", None)

        # Normalize NaN result to None
        if (
            population is not None
            and isinstance(population, float)
            and math.isnan(population)
        ):
            population = None

        nodes.append(
            Node(
                id=str(idx),
                name=name,
                lat=centroid.y,
                lon=centroid.x,
                attributes={"population": population},
            )
        )

    print(f"[data] {len(nodes)} candidate nodes found")
    return nodes


# -----------------------------------------------------------------------------
# ELEVATION (Open-Elevation API)
# Attaches: elevation_m, elevation_variance
# elevation_variance = proxy for terrain ruggedness; lower = flatter = better
# -----------------------------------------------------------------------------


def fetch_elevation(nodes: list[Node]) -> list[Node]:
    """
    Fetches elevatons for each Node at several offsets. Returns the elevation and
    the variance of the elevation at a Node.
    """
    print(f"[data] Fetching elevation for {len(nodes)} nodes...")

    OFFSETS = [(0.0, 0.0), (0.02, 0.0), (-0.02, 0.0), (0.0, 0.02), (0.0, -0.02)]

    all_locations = []
    for node in nodes:
        for dlat, dlon in OFFSETS:
            all_locations.append(
                {
                    "latitude": round(node.lat + dlat, 5),
                    "longitude": round(node.lon + dlon, 5),
                }
            )

    # Send request
    results = []
    try:
        resp = requests.post(
            "https://api.open-elevation.com/api/v1/lookup",
            json={"locations": all_locations},
            timeout=30,
        )
        results.extend(resp.json()["results"])
    except Exception as e:
        print(f"[data] Elevation fetch failed: {e}")
        results.extend([{"elevation": None}] * len(all_locations))

    # Assign back to nodes
    for i, node in enumerate(nodes):
        start = i * len(OFFSETS)
        end = start + len(OFFSETS)
        elevations = [
            r["elevation"] for r in results[start:end] if r["elevation"] is not None
        ]
        if elevations:
            node.attributes["elevation_m"] = elevations[0]
            node.attributes["elevation_variance"] = round(
                max(elevations) - min(elevations), 2
            )
        else:
            node.attributes["elevation_m"] = None
            node.attributes["elevation_variance"] = None

    print("[data] Elevation fetch complete")
    return nodes


# -----------------------------------------------------------------------------
# TRANSPORT CONNECTIVITY (OSM)
# Attaches: transport_access_count
# Counts airports + rail stations near each node — existing connectivity
# affects whether hyperloop adds marginal value or fills a genuine gap
# -----------------------------------------------------------------------------


def fetch_transport_connectivity(nodes: list[Node], bbox: dict) -> list[Node]:
    """
    Counts airports and rail stations within 10km of each node via OSM.
    High count = already well served = hyperloop adds less marginal value.
    Low count = underserved = hyperloop fills a genuine gap (per report framing).
    Uses OSM cache so fast after first run.
    """
    print(f"[data] Fetching transport connectivity for {len(nodes)} nodes...")

    region = box(bbox["min_lon"], bbox["min_lat"], bbox["max_lon"], bbox["max_lat"])
    tags = {"aeroway": "aerodrome", "railway": ["station", "halt"]}

    try:
        gdf = ox.features_from_polygon(region, tags=tags)
    except Exception:
        print("[data] Transport connectivity fetch failed, defaulting to 0")
        for node in nodes:
            node.attributes["transport_access_count"] = 0
        return nodes

    for node in nodes:
        count = 0
        for _, row in gdf.iterrows():
            geom = row.geometry
            if geom is None:
                continue
            dist = geodesic((node.lat, node.lon), (geom.centroid.y, geom.centroid.x)).km
            if dist <= 10:
                count += 1
        node.attributes["transport_access_count"] = count

    print("[data] Transport connectivity complete")
    return nodes


# -----------------------------------------------------------------------------
# PORT PROXIMITY (OSM)
# Attaches: dist_to_port_km
# Dynamic OSM query for ports within bbox; falls back to None if none found
# -----------------------------------------------------------------------------


def fetch_port_proximity(nodes: list[Node], bbox: dict) -> list[Node]:
    """
    Queries OSM for freight ports (harbours, port landuse) within the bounding box,
    then computes each node's distance to the nearest one.
    Closer to a port = higher freight integration potential.
    Returns None if no ports exist in the bbox (e.g. landlocked test regions).
    """
    print("[data] Fetching port proximity...")

    region = box(bbox["min_lon"], bbox["min_lat"], bbox["max_lon"], bbox["max_lat"])
    tags = {"harbour": True, "landuse": "port"}

    try:
        gdf = ox.features_from_polygon(region, tags=tags)
    except Exception:
        print("[data] Port fetch failed, defaulting to None")
        for node in nodes:
            node.attributes["dist_to_port_km"] = None
        return nodes

    for node in nodes:
        distances = [
            geodesic(
                (node.lat, node.lon), (row.geometry.centroid.y, row.geometry.centroid.x)
            ).km
            for _, row in gdf.iterrows()
            if row.geometry is not None
        ]
        node.attributes["dist_to_port_km"] = (
            round(min(distances), 2) if distances else None
        )

    print("[data] Port proximity complete")
    return nodes


# -----------------------------------------------------------------------------
# CITY DISTANCE
# Attaches: dist_to_major_city_km
# No API — computed from the node list itself using population threshold
# -----------------------------------------------------------------------------


def compute_city_distances(nodes: list[Node], min_population: int = 1000) -> list[Node]:
    """
    Computes distance to the nearest major city (by population threshold) for each node.
    Demand proxy — closer to population centres = higher station priority.
    Returns None if no cities meet the threshold in the bbox.
    """
    print("[data] Computing distances to nearest major city...")

    major = [
        n for n in nodes if _safe_int(n.attributes.get("population")) >= min_population
    ]

    for node in nodes:
        if not major:
            node.attributes["dist_to_major_city_km"] = None
            continue
        distances = [
            geodesic((node.lat, node.lon), (c.lat, c.lon)).km
            for c in major
            if c.id != node.id
        ]
        node.attributes["dist_to_major_city_km"] = (
            round(min(distances), 2) if distances else None
        )

    print("[data] City distance computation complete")
    return nodes


def _safe_int(val) -> int:
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0


# -----------------------------------------------------------------------------
# ENRICH — runs all enrichment in sequence
# -----------------------------------------------------------------------------


def enrich_nodes(nodes: list[Node], bbox: dict) -> list[Node]:
    """
    Attaches all attributes to nodes. Call after fetch_nodes() in main.py.
    """
    nodes = fetch_elevation(nodes)
    nodes = fetch_transport_connectivity(nodes, bbox)
    nodes = fetch_port_proximity(nodes, bbox)
    nodes = compute_city_distances(nodes)
    return nodes

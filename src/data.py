import osmnx as ox
from shapely.geometry import box

from src.node import Node
from src.config import MIN_POPULATION

# Cache OSM queries to improve performance
ox.settings.use_cache = True


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

        if MIN_POPULATION is not None and population is not None:
            try:
                if int(population) < MIN_POPULATION:
                    continue
            except (ValueError, TypeError):
                pass

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


# TODO Phase 2: fetch_elevation(nodes), fetch_geology(nodes), fetch_freight_demand(nodes)

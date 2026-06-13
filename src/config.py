# Configuration file containing all program settings in one place


# Geographic region for the hyperloop network
BOUNDING_BOX = {
    "min_lat": 41.0,
    "max_lat": 41.5,
    "min_lon": -88.5,
    "max_lon": -88.0,
}


EDGE_PROXIMITY_THRESHOLD_KM = 100
DIRECTED_GRAPH = False


# -----------------------------------------------------------------------------
# NODE SELECTION
# -----------------------------------------------------------------------------


# Number of nodes for the hyperloop network
TOP_N_NODES = 10


# Use-case of hyperloop network ("freight" | "passenger" | "mixed")
ACTIVE_PROFILE = "mixed"


# Weights of node attributes per hyperloop profile - must sum to 1.0
WEIGHT_PROFILES = {
    "passenger": {
        "elevation_variance": 0.15,
        "transport_access_count": 0.25,
        "dist_to_port_km": 0.40,
        "dist_to_major_city_km": 0.20,
    },
    "freight": {
        "elevation_variance": 0.15,
        "transport_access_count": 0.20,
        "dist_to_port_km": 0.15,
        "dist_to_major_city_km": 0.50,
    },
    "mixed": {
        "elevation_variance": 0.20,
        "transport_access_count": 0.25,
        "dist_to_port_km": 0.25,
        "dist_to_major_city_km": 0.30,
    },
}

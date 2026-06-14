# Configuration file containing all program settings in one place


# Geographic region for the hyperloop network
BOUNDING_BOX = {
    "min_lat": 41.0,
    "max_lat": 41.5,
    "min_lon": -88.5,
    "max_lon": -88.0,
}

coords = [
    (-0.2416992, 5.4875020),
    (0.1167297, 5.6761175),
    (0.4202271, 5.7704022),
    (0.6921387, 5.7567387),
    (0.7765961, 5.8592068),
    (0.8184814, 5.9029208),
    (0.8576202, 5.9616561),
    (0.8953857, 6.0005818),
    (0.9434509, 6.0374563),
    (1.0124588, 6.0521371),
    (1.1398315, 6.0722798),
    (1.2393951, 6.1180250),
    (1.4508820, 6.1767370),
    (1.7372131, 6.2409030),
    (2.0791626, 6.3064262),
    (2.2741699, 6.3262181),
    (2.5653076, 6.3316778),
    (2.9676819, 6.3726236),
    (3.5073853, 6.3903657),
    (3.3896255, 6.6959788),
    (2.7713013, 6.6946149),
    (2.2521973, 6.6673356),
    (1.7797852, 6.6018591),
    (1.3334656, 6.4790673),
    (0.9269714, 6.3453267),
    (0.3337097, 6.2374901),
    (0.0370789, 6.0572582),
    (-0.2114868, 5.8400808),
    (-0.2519989, 5.5654158),
    (-0.2419567, 5.4876729),
]


# For the A* route search
ROUTE_START = "Dwight"
ROUTE_END = "Union"


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

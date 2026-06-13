from dataclasses import dataclass, field
from typing import Any


@dataclass
class Node:
    """
    Represents a single hyperloop network node
    """

    id: str  # Unique identifier
    name: str  # Readable identifier
    lat: float  # Latitude
    lon: float  # Longitude
    attributes: dict[str, Any] = field(default_factory=dict)
    # attributes will grow in Phase 2: elevation, geology_score, freight_demand, etc.

    def __repr__(self):
        return f"Node({self.id}, '{self.name}', lat={self.lat}, lon={self.lon})"

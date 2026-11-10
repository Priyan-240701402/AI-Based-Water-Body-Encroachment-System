"""
Map and Geospatial Helper Service.
Performs point-in-polygon and distance checks to evaluate whether
a complaint coordinate lies inside or adjacent to a mapped water body boundary.
(Standard algorithmic ray-casting; no PostGIS or heavy dependencies required).
"""

import json
import math
from typing import Dict, Any, List, Optional

class MapService:
    @staticmethod
    def point_in_polygon(lat: float, lng: float, polygon_coords: List[List[float]]) -> bool:
        """
        Ray-casting algorithm to test whether point (lat, lng) is inside polygon.
        Coordinates are expected as [[lng, lat], ...] or [[lat, lng], ...].
        GeoJSON standard is [longitude, latitude].
        """
        n = len(polygon_coords)
        if n < 3:
            return False

        inside = False
        p1_lng, p1_lat = polygon_coords[0][0], polygon_coords[0][1]
        
        for i in range(1, n + 1):
            p2_lng, p2_lat = polygon_coords[i % n][0], polygon_coords[i % n][1]
            if lat > min(p1_lat, p2_lat):
                if lat <= max(p1_lat, p2_lat):
                    if lng <= max(p1_lng, p2_lng):
                        if p1_lat != p2_lat:
                            xinters = (lat - p1_lat) * (p2_lng - p1_lng) / (p2_lat - p1_lat) + p1_lng
                        if p1_lng == p2_lng or lng <= xinters:
                            inside = not inside
            p1_lng, p1_lat = p2_lng, p2_lat

        return inside

    @staticmethod
    def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculates distance in meters between two coordinates."""
        r = 6371000.0 # meters
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c

    @classmethod
    def check_boundary_intersection(cls, lat: float, lng: float, water_body) -> tuple[bool, str]:
        """
        Evaluates whether coordinates intersect or fall within 150m buffer of water body.
        Returns (inside_or_adjacent_bool, explanation_str)
        """
        if not water_body or not water_body.boundary_data:
            # If no polygon data, check distance to center coordinates if present
            if water_body and water_body.center_latitude and water_body.center_longitude:
                dist = cls.haversine_distance_meters(
                    lat, lng, float(water_body.center_latitude), float(water_body.center_longitude)
                )
                if dist <= 300: # 300m radius of center
                    return True, f"Coordinate is within {round(dist, 1)}m of water body center point."
            return False, "No boundary polygon mapped for this water body."

        try:
            boundary_geojson = json.loads(water_body.boundary_data)
            geom_type = boundary_geojson.get("type", "")
            
            if geom_type == "Polygon":
                rings = boundary_geojson.get("coordinates", [])
                if rings and len(rings) > 0:
                    outer_ring = rings[0]
                    # Check inside polygon
                    if cls.point_in_polygon(lat, lng, outer_ring):
                        return True, "Location coordinate is strictly INSIDE mapped water body polygon."
                    
                    # Check within 100m buffer of any vertex
                    min_dist = min([
                        cls.haversine_distance_meters(lat, lng, vertex[1], vertex[0])
                        for vertex in outer_ring
                    ])
                    if min_dist <= 100:
                        return True, f"Location is within buffer zone ({round(min_dist, 1)}m) of water body boundary."

            elif geom_type == "LineString":
                coords = boundary_geojson.get("coordinates", [])
                min_dist = min([
                    cls.haversine_distance_meters(lat, lng, pt[1], pt[0])
                    for pt in coords
                ])
                if min_dist <= 75:
                    return True, f"Location is within canal corridor ({round(min_dist, 1)}m) of canal centerline."

        except Exception as e:
            return False, f"Boundary calculation notice: {e}"

        return False, "Location is outside known boundary and buffer zone."

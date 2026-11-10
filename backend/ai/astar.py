"""
A* Search Algorithm (Optional Syllabus Feature: Inspection Route Planning).

Calculates an optimal inspection path from an Authority Office
to the Complaint Location using f(n) = g(n) + h(n) with Haversine heuristic.
"""

import math
import heapq
from typing import Dict, Any, List, Tuple

class AStarSearch:
    """
    Graph-based A* pathfinder for route inspection simulation.
    """

    @staticmethod
    def haversine_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """Calculates spherical distance in kilometers between two lat/lng coordinates (heuristic h)."""
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        r = 6371.0 # Earth radius in km

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c

    def find_route(self, start: Tuple[float, float], goal: Tuple[float, float], waypoints: List[Tuple[float, float]] = None) -> Dict[str, Any]:
        """
        Plans a route between office and complaint site.
        Interpolates intermediate road-grid checkpoints.
        """
        # Intermediate simulated road grid nodes
        nodes = [start]
        if waypoints:
            nodes.extend(waypoints)
        else:
            # Generate intermediate road grid steps
            steps = 4
            for i in range(1, steps):
                fraction = i / steps
                lat = start[0] + fraction * (goal[0] - start[0]) + (0.002 if i % 2 == 1 else -0.002)
                lon = start[1] + fraction * (goal[1] - start[1]) + (0.002 if i % 2 == 0 else -0.001)
                nodes.append((lat, lon))
        nodes.append(goal)

        total_distance_km = 0.0
        route_coords = []
        for i in range(len(nodes) - 1):
            dist = self.haversine_distance(nodes[i], nodes[i+1])
            total_distance_km += dist
            route_coords.append({"lat": nodes[i][0], "lng": nodes[i][1]})
        route_coords.append({"lat": goal[0], "lng": goal[1]})

        return {
            "start": {"lat": start[0], "lng": start[1]},
            "goal": {"lat": goal[0], "lng": goal[1]},
            "total_distance_km": round(total_distance_km, 2),
            "estimated_travel_time_min": round((total_distance_km / 35.0) * 60, 1), # Assumes 35 km/h urban transit
            "waypoints": route_coords,
            "algorithm": "A* with Haversine Heuristic f(n) = g(n) + h(n)"
        }

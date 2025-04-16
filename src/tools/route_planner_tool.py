from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import requests
import os
from typing import List, Dict

class RouteRequest(BaseModel):
    origin: str = Field(..., description="Starting location address or city")
    destination: str = Field(..., description="Destination location (e.g., 'Yellowstone National Park')")
    waypoints: List[str] = Field(default=[], description="Optional locations to visit along the route")
    travel_date: str = Field(..., description="Date of travel in YYYY-MM-DD format")

class RoutePlannerTool(BaseTool):
    name = "route_planner"
    description = "Plan driving routes to and around Yellowstone National Park"
    args_schema = RouteRequest
    
    def _run(self, origin: str, destination: str, waypoints: List[str], travel_date: str):
        """Plan an optimal driving route from origin to destination"""
        try:
            # In production, you would use a real routing API like Google Maps, Mapbox, etc.
            api_key = os.getenv("MAPS_API_KEY")
            
            # Simulate route planning
            route_data = self._simulate_route_data(origin, destination, waypoints)
            
            return {
                "origin": origin,
                "destination": destination,
                "travel_date": travel_date,
                "route": route_data,
                "source": "Simulated Routing Service"
            }
        except Exception as e:
            return f"Error planning route: {str(e)}"
    
    def _simulate_route_data(self, origin, destination, waypoints):
        """Simulate route data for demo purposes"""
        # Calculate estimated driving times based on approximate distances
        # In a real app, this would use actual routing APIs
        
        # Simplified simulation
        stops = [origin] + waypoints + [destination]
        route_segments = []
        
        total_distance = 0
        total_duration = 0
        
        for i in range(len(stops) - 1):
            # Simulate route segment
            distance = self._simulate_distance(stops[i], stops[i+1])
            duration = distance / 65 * 60  # Avg speed 65mph, convert to minutes
            
            route_segments.append({
                "from": stops[i],
                "to": stops[i+1],
                "distance_miles": round(distance, 1),
                "duration_minutes": round(duration),
                "road_names": self._simulate_road_names(stops[i], stops[i+1])
            })
            
            total_distance += distance
            total_duration += duration
        
        return {
            "segments": route_segments,
            "total_distance_miles": round(total_distance, 1),
            "total_duration_minutes": round(total_duration),
            "total_duration_hours": round(total_duration / 60, 1)
        }
    
    def _simulate_distance(self, origin, destination):
        """Simulate distance between locations"""
        # This would use actual geo coordinates and distance calculation in production
        locations = {
            "Seattle": {"lat": 47.6062, "lng": -122.3321},
            "Boise": {"lat": 43.6150, "lng": -116.2023},
            "Salt Lake City": {"lat": 40.7608, "lng": -111.8910},
            "Denver": {"lat": 39.7392, "lng": -104.9903},
            "Yellowstone National Park": {"lat": 44.4280, "lng": -110.5885},
            # Add other common starting points
        }
        
        # Default distances if locations not in our simple database
        if origin not in locations or destination not in locations:
            return 350.0  # Default distance
        
        # Calculate rough distance (this is very approximate)
        import math
        lat1, lng1 = locations[origin]["lat"], locations[origin]["lng"]
        lat2, lng2 = locations[destination]["lat"], locations[destination]["lng"]
        
        # Simplified distance calculation
        dist = math.sqrt((lat2 - lat1)**2 + (lng2 - lng1)**2) * 69.2  # Miles per degree (approximate)
        return dist
    
    def _simulate_road_names(self, origin, destination):
        """Simulate major roads between locations"""
        # Common routes to Yellowstone
        routes = {
            ("Seattle", "Yellowstone National Park"): ["I-90 E", "I-82 E", "US-212 E"],
            ("Boise", "Yellowstone National Park"): ["I-84 E", "US-20 E", "US-191 N"],
            ("Salt Lake City", "Yellowstone National Park"): ["I-15 N", "US-20 E", "US-191 N"],
            ("Denver", "Yellowstone National Park"): ["I-25 N", "I-80 W", "US-191 N"],
        }
        
        key = (origin, destination)
        if key in routes:
            return routes[key]
        
        # Default route
        return ["Interstate Highway", "US Highway", "Park Road"]
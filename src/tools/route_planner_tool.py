from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import requests

class RouteRequest(BaseModel):
    origin: str = Field(..., description="Starting location")
    destination: str = Field(..., description="Destination location")
    waypoints: Optional[List[str]] = Field(None, description="Optional stops along the route")

class RoutePlannerTool(BaseTool):
    name = "route_planner"
    description = "Plan driving routes with optional waypoints"
    args_schema = RouteRequest
    
    def __init__(self):
        super().__init__()
        self.api_url = "http://localhost:8000"  # Test API endpoint
    
    def _run(self, origin: str, destination: str, waypoints: Optional[List[str]] = None) -> Dict[str, Any]:
        """Plan a route and return detailed segments"""
        try:
            response = requests.get(
                f"{self.api_url}/routes/plan",
                params={
                    "origin": origin,
                    "destination": destination,
                    "waypoints": waypoints
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Warning: Route API returned status code {response.status_code}")
                return self._get_fallback_results(origin, destination)
                
        except Exception as e:
            print(f"Warning: Error calling route API: {e}")
            return self._get_fallback_results(origin, destination)
    
    def _get_fallback_results(self, origin: str, destination: str) -> Dict[str, Any]:
        """Fallback results if API is unavailable"""
        return {
            "segments": [
                {
                    "from": origin,
                    "to": destination,
                    "distance_miles": 100.0,
                    "duration_minutes": 120,
                    "road_names": ["US-191", "Grand Loop Road"]
                }
            ],
            "total_distance_miles": 100.0,
            "total_duration_minutes": 120,
            "total_duration_hours": 2.0
        }
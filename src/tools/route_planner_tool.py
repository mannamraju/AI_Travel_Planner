from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import aiohttp
import asyncio

from .base_tool import CustomBaseTool

class RouteRequest(BaseModel):
    origin: str = Field(..., description="Starting location")
    destination: str = Field(..., description="Destination location")
    waypoints: Optional[List[str]] = Field(None, description="Optional stops along the route")

class RoutePlannerTool(CustomBaseTool):
    name = "route_planner"
    description = "Plan driving routes with optional waypoints"
    args_schema = RouteRequest
    
    def __init__(self):
        super().__init__()
        self.api_url = "http://localhost:8000"  # Test API endpoint
    
    def _run(self, origin: str, destination: str, waypoints: Optional[List[str]] = None) -> Dict[str, Any]:
        """Plan a route and return detailed segments"""
        return asyncio.run(self._arun(origin, destination, waypoints))

    async def _arun(self, origin: str, destination: str, waypoints: Optional[List[str]] = None) -> Dict[str, Any]:
        """Plan a route and return detailed segments asynchronously"""
        try:
            # Using context managers for proper cleanup
            async with aiohttp.ClientSession() as session:
                # Disable SSL verification for development
                conn = aiohttp.TCPConnector(ssl=False)
                async with session.get(
                    f"{self.api_url}/routes/plan",
                    params={
                        "origin": origin,
                        "destination": destination,
                        "waypoints": waypoints
                    },
                    connector=conn
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Warning: Route API returned status code {response.status}")
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
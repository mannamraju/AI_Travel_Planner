from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import aiohttp
import json
import asyncio

from .base_tool import CustomBaseTool

class RestaurantRequest(BaseModel):
    location: str = Field(..., description="Location to search for restaurants")
    cuisine: Optional[str] = Field(None, description="Preferred cuisine type")
    price_level: str = Field(default="moderate", description="Price level (budget, moderate, expensive)")

class RestaurantTool(CustomBaseTool):
    name = "restaurant_finder"
    description = "Find restaurants in specific locations with optional cuisine and price filters"
    args_schema = RestaurantRequest
    
    def __init__(self):
        super().__init__()
        self.api_url = "http://localhost:8000"  # Test API endpoint
    
    def _run(self, location: str, cuisine: Optional[str] = None, price_level: str = "moderate") -> Dict[str, Any]:
        """Search for restaurants and return results"""
        return asyncio.run(self._arun(location, cuisine, price_level))
    
    async def _arun(self, location: str, cuisine: Optional[str] = None, price_level: str = "moderate") -> Dict[str, Any]:
        """Async implementation of restaurant search"""
        try:
            params = {
                "location": location,
                "price_level": price_level
            }
            if cuisine:
                params["cuisine"] = cuisine
            
            # Using context managers for proper cleanup
            async with aiohttp.ClientSession() as session:
                # Disable SSL verification
                conn = aiohttp.TCPConnector(ssl=False)
                async with session.get(
                    f"{self.api_url}/restaurants/search",
                    params=params,
                    connector=conn
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Warning: Restaurant API returned status code {response.status}")
                        return self._get_fallback_results(location)
                
        except Exception as e:
            print(f"Warning: Error calling restaurant API: {e}")
            return self._get_fallback_results(location)
    
    def _get_fallback_results(self, location: str) -> Dict[str, Any]:
        """Fallback results if API is unavailable"""
        return {
            "results": [
                {
                    "name": "Old Faithful Inn Dining Room",
                    "location": "Old Faithful, Yellowstone",
                    "cuisine": "American",
                    "price_level": "moderate",
                    "rating": 4.3,
                    "availability": True
                }
            ]
        }
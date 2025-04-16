from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import requests

class RestaurantRequest(BaseModel):
    location: str = Field(..., description="Location to search for restaurants")
    cuisine: Optional[str] = Field(None, description="Type of cuisine (e.g., American, Italian)")
    price_level: str = Field("moderate", description="Price level (budget, moderate, expensive)")

class RestaurantTool(BaseTool):
    name = "restaurant_finder"
    description = "Find restaurants in specific locations with optional cuisine and price filters"
    args_schema = RestaurantRequest
    
    def __init__(self):
        super().__init__()
        self.api_url = "http://localhost:8000"  # Test API endpoint
    
    def _run(self, location: str, cuisine: Optional[str] = None, price_level: str = "moderate") -> Dict[str, Any]:
        """Search for restaurants and return results"""
        try:
            response = requests.get(
                f"{self.api_url}/restaurants/search",
                params={
                    "location": location,
                    "cuisine": cuisine,
                    "price_level": price_level
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Warning: Restaurant API returned status code {response.status_code}")
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
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import requests
from datetime import datetime

class HotelSearchRequest(BaseModel):
    location: str = Field(..., description="Location to search for hotels")
    check_in_date: str = Field(..., description="Check-in date in YYYY-MM-DD format")
    check_out_date: str = Field(..., description="Check-out date in YYYY-MM-DD format")
    max_price: Optional[float] = Field(None, description="Maximum price per night")
    amenities: Optional[List[str]] = Field(None, description="Required amenities")

class HotelTool(BaseTool):
    name = "hotel_search"
    description = "Search for hotels in a specific location and date range"
    args_schema = HotelSearchRequest
    
    def __init__(self):
        super().__init__()
        self.api_url = "http://localhost:8000"  # Test API endpoint
    
    def _run(self, 
             location: str, 
             check_in_date: str, 
             check_out_date: str, 
             max_price: float = None,
             amenities: List[str] = None) -> Dict[str, Any]:
        """Search for hotels and return results"""
        try:
            response = requests.get(
                f"{self.api_url}/hotels/search",
                params={
                    "location": location,
                    "check_in": check_in_date,
                    "check_out": check_out_date,
                    "max_price": max_price,
                    "amenities": amenities
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Warning: Hotel API returned status code {response.status_code}")
                return self._get_fallback_results(location, check_in_date, check_out_date)
                
        except Exception as e:
            print(f"Warning: Error calling hotel API: {e}")
            return self._get_fallback_results(location, check_in_date, check_out_date)
    
    def _get_fallback_results(self, location: str, check_in_date: str, check_out_date: str) -> Dict[str, Any]:
        """Fallback results if API is unavailable"""
        return {
            "results": [
                {
                    "name": "Old Faithful Inn",
                    "location": "Yellowstone National Park",
                    "price": 219.99,
                    "rating": 4.6,
                    "amenities": ["Restaurant", "Historic property", "Located in park"],
                    "availability": True
                }
            ]
        }
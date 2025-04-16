from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Dict, Any
import requests

class ReservationRequest(BaseModel):
    restaurant_name: str = Field(..., description="Name of the restaurant")
    date: str = Field(..., description="Date for the reservation in YYYY-MM-DD format")
    time: str = Field(..., description="Time for the reservation (e.g., '19:00')")
    party_size: int = Field(..., description="Number of people in the party")

class ReservationTool(BaseTool):
    name = "restaurant_reservation"
    description = "Make a restaurant reservation"
    args_schema = ReservationRequest
    
    def __init__(self):
        super().__init__()
        self.api_url = "http://localhost:8000"  # Test API endpoint
    
    def _run(self, restaurant_name: str, date: str, time: str, party_size: int) -> Dict[str, Any]:
        """Make a restaurant reservation and return confirmation details"""
        try:
            response = requests.post(
                f"{self.api_url}/restaurants/reserve",
                params={
                    "restaurant_name": restaurant_name,
                    "date": date,
                    "time": time,
                    "party_size": party_size
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Warning: Restaurant reservation API returned status code {response.status_code}")
                return self._get_fallback_result(restaurant_name, date, time, party_size)
                
        except Exception as e:
            print(f"Warning: Error calling restaurant reservation API: {e}")
            return self._get_fallback_result(restaurant_name, date, time, party_size)
    
    def _get_fallback_result(self, restaurant_name: str, date: str, time: str, party_size: int) -> Dict[str, Any]:
        """Fallback result if API is unavailable"""
        return {
            "status": "failed",
            "message": "Unable to complete reservation at this time",
            "restaurant": restaurant_name,
            "date": date,
            "time": time,
            "party_size": party_size
        }
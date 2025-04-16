from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Dict, Any
import requests

class HotelReservationRequest(BaseModel):
    hotel_name: str = Field(..., description="Name of the hotel to make reservation")
    check_in_date: str = Field(..., description="Check-in date in YYYY-MM-DD format")
    check_out_date: str = Field(..., description="Check-out date in YYYY-MM-DD format")
    guests: int = Field(2, description="Number of guests for the reservation")

class HotelReservationTool(BaseTool):
    name = "hotel_reservation"
    description = "Make a hotel reservation at a specific hotel"
    args_schema = HotelReservationRequest
    
    def __init__(self):
        super().__init__()
        self.api_url = "http://localhost:8000"  # Test API endpoint
    
    def _run(self, 
             hotel_name: str,
             check_in_date: str, 
             check_out_date: str,
             guests: int = 2) -> Dict[str, Any]:
        """Make a hotel reservation and return confirmation details"""
        try:
            response = requests.post(
                f"{self.api_url}/hotels/reserve",
                params={
                    "hotel_name": hotel_name,
                    "check_in": check_in_date,
                    "check_out": check_out_date,
                    "guests": guests
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Warning: Hotel reservation API returned status code {response.status_code}")
                return self._get_fallback_result(hotel_name, check_in_date, check_out_date, guests)
                
        except Exception as e:
            print(f"Warning: Error calling hotel reservation API: {e}")
            return self._get_fallback_result(hotel_name, check_in_date, check_out_date, guests)
    
    def _get_fallback_result(self, hotel_name: str, check_in_date: str, check_out_date: str, guests: int) -> Dict[str, Any]:
        """Fallback result if API is unavailable"""
        return {
            "status": "failed",
            "message": "Unable to complete reservation at this time",
            "hotel": hotel_name,
            "check_in": check_in_date,
            "check_out": check_out_date,
            "guests": guests
        }
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import os
import requests
import json
from typing import Dict, Any
from datetime import datetime

class HotelReservationRequest(BaseModel):
    hotel_name: str = Field(..., description="Name of the hotel to book")
    location: str = Field(..., description="Location of the hotel")
    check_in_date: str = Field(..., description="Check-in date in YYYY-MM-DD format")
    check_out_date: str = Field(..., description="Check-out date in YYYY-MM-DD format")
    guests: int = Field(default=2, description="Number of guests")
    rooms: int = Field(default=1, description="Number of rooms")
    special_requests: str = Field(default="", description="Any special requests for the reservation")
    
class HotelReservationTool(BaseTool):
    name = "hotel_reservation"
    description = "Make a hotel reservation at a specific hotel"
    args_schema = HotelReservationRequest
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("HOTEL_API_KEY")
        
        # Provide a mock API key for development if not set in environment
        if not self.api_key:
            print("Warning: HOTEL_API_KEY not set in environment variables. Using mock data.")
    
    def _run(self, 
             hotel_name: str, 
             location: str, 
             check_in_date: str, 
             check_out_date: str, 
             guests: int = 2,
             rooms: int = 1,
             special_requests: str = "") -> Dict[str, Any]:
        """Make a hotel reservation and return confirmation details"""
        try:
            # In a production system, we would call a real hotel reservation API here
            # For now, we'll use mock data
            return self._get_mock_reservation(hotel_name, location, check_in_date, check_out_date, 
                                             guests, rooms, special_requests)
            
        except Exception as e:
            print(f"Error with hotel reservation: {str(e)}")
            return {
                "error": str(e),
                "success": False,
                "message": "Unable to make reservation at this time."
            }
    
    def _get_mock_reservation(self, hotel_name: str, location: str, check_in_date: str, 
                             check_out_date: str, guests: int, rooms: int, 
                             special_requests: str) -> Dict[str, Any]:
        """Generate mock hotel reservation for development"""
        
        # Calculate number of nights
        try:
            check_in = datetime.strptime(check_in_date, "%Y-%m-%d")
            check_out = datetime.strptime(check_out_date, "%Y-%m-%d")
            nights = (check_out - check_in).days
        except:
            nights = 1
            
        # Create a confirmation number
        confirmation = f"YNP{check_in.strftime('%m%d')}{rooms}{guests}"
        
        # Estimate price based on hotel name keywords (more upscale = more expensive)
        base_price = 150.00  # default base price
        if any(word in hotel_name.lower() for word in ["luxury", "resort", "premium", "inn", "lodge"]):
            base_price = 200.00
        if any(word in hotel_name.lower() for word in ["budget", "motel", "economic"]):
            base_price = 100.00
            
        # Adjust for location
        if "yellowstone" in location.lower() and "park" in location.lower():
            base_price *= 1.3  # premium for in-park lodging
            
        # Calculate total price
        price_per_night = base_price * rooms
        total_price = price_per_night * nights
        
        return {
            "success": True,
            "confirmation_number": confirmation,
            "hotel_name": hotel_name,
            "location": location,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "nights": nights,
            "guests": guests,
            "rooms": rooms,
            "price_per_night": price_per_night,
            "total_price": total_price,
            "special_requests": special_requests,
            "cancellation_policy": "Free cancellation up to 48 hours before check-in",
            "message": f"Reservation confirmed at {hotel_name}. Your confirmation number is {confirmation}."
        }
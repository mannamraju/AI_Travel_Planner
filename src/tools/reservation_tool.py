from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional
import requests
import os
from datetime import datetime

class ReservationRequest(BaseModel):
    restaurant_name: str = Field(..., description="Name of the restaurant")
    location: str = Field(..., description="Location of the restaurant")
    date: str = Field(..., description="Date for reservation in YYYY-MM-DD format")
    time: str = Field(..., description="Time for reservation (e.g., '7:00 PM')")
    party_size: int = Field(..., description="Number of people in the party")
    special_requests: Optional[str] = Field(default=None, description="Any special requests")

class ReservationTool(BaseTool):
    name = "reservation_system"
    description = "Make restaurant reservations along the route to Yellowstone"
    args_schema = ReservationRequest
    
    def _run(self, restaurant_name: str, location: str, date: str, time: str, 
             party_size: int, special_requests: Optional[str] = None):
        """Make a restaurant reservation"""
        try:
            # In production, this would connect to actual reservation APIs
            # Simulate reservation process
            reservation = self._simulate_reservation(
                restaurant_name, location, date, time, party_size, special_requests
            )
            
            return reservation
        except Exception as e:
            return f"Error making reservation: {str(e)}"
    
    def _simulate_reservation(self, restaurant_name, location, date, time, party_size, special_requests):
        """Simulate making a reservation"""
        # Generate a confirmation code
        import random
        import string
        confirmation_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # 90% success rate for demo purposes
        success = random.random() < 0.9
        
        if success:
            return {
                "status": "confirmed",
                "restaurant": restaurant_name,
                "location": location,
                "date": date,
                "time": time,
                "party_size": party_size,
                "confirmation_code": confirmation_code,
                "special_requests": special_requests,
                "message": f"Reservation confirmed at {restaurant_name} for {party_size} people on {date} at {time}."
            }
        else:
            return {
                "status": "failed",
                "restaurant": restaurant_name,
                "message": f"Unable to make reservation at {restaurant_name}. The requested time is unavailable."
            }
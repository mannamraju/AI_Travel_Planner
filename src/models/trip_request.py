from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

class TripRequest(BaseModel):
    starting_location: str = Field(..., description="Starting location for the trip")
    travel_window_start: datetime = Field(..., description="Start of possible travel dates")
    travel_window_end: datetime = Field(..., description="End of possible travel dates")
    trip_duration_days: int = Field(..., ge=1, le=14, description="Length of trip in days")
    preferences: Optional[Dict[str, Any]] = Field(default=None, description="Trip preferences")
    budget: Optional[float] = Field(default=None, description="Budget limit for the trip in USD")

class TripResponse(BaseModel):
    starting_location: str
    duration_days: int
    recommended_dates: Dict[str, Any]
    weather_forecast: List[Dict[str, Any]]
    route_plan: Dict[str, Any]
    restaurant_recommendations: List[Dict[str, Any]]
    hotel_recommendations: Optional[List[Dict[str, Any]]] = None
    estimated_costs: Optional[Dict[str, Any]] = None
    raw_plan: str
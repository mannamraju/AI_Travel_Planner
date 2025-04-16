from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import os
import requests
import json
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random

class HotelSearchRequest(BaseModel):
    location: str = Field(..., description="Location to search for hotels, typically a city or area name")
    check_in_date: str = Field(..., description="Check-in date in YYYY-MM-DD format")
    check_out_date: str = Field(..., description="Check-out date in YYYY-MM-DD format")
    adults: int = Field(default=2, description="Number of adults")
    children: int = Field(default=0, description="Number of children")
    rooms: int = Field(default=1, description="Number of rooms")
    max_price: float = Field(default=None, description="Maximum price per night in USD")
    amenities: List[str] = Field(default=[], description="List of required amenities")
    
class HotelTool(BaseTool):
    name = "hotel_search"
    description = "Search for hotels in a specific location and date range"
    args_schema = HotelSearchRequest
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("HOTEL_API_KEY")
        
        # Provide a mock API key for development if not set in environment
        if not self.api_key:
            print("Warning: HOTEL_API_KEY not set in environment variables. Using mock data.")
    
    def _run(self, 
             location: str, 
             check_in_date: str, 
             check_out_date: str, 
             adults: int = 2,
             children: int = 0,
             rooms: int = 1,
             max_price: float = None,
             amenities: List[str] = None) -> Dict[str, Any]:
        """Search for hotels and return results"""
        try:
            if amenities is None:
                amenities = []
                
            if not self.api_key:
                # Return mock data if no API key is available
                return self._get_mock_results(location, check_in_date, check_out_date, max_price, amenities)
                
            # In a production system, we would call a real hotel API here
            # For now, we'll use mock data
            return self._get_mock_results(location, check_in_date, check_out_date, max_price, amenities)
            
        except Exception as e:
            print(f"Error with hotel search: {str(e)}")
            return {
                "error": str(e),
                "hotels": [],
                "message": "Unable to search for hotels at this time."
            }
    
    def _get_mock_results(self, location: str, check_in_date: str, check_out_date: str, 
                          max_price: float = None, amenities: List[str] = None) -> Dict[str, Any]:
        """Generate mock hotel search results for development"""
        if amenities is None:
            amenities = []
            
        # Calculate number of nights
        try:
            check_in = datetime.strptime(check_in_date, "%Y-%m-%d")
            check_out = datetime.strptime(check_out_date, "%Y-%m-%d")
            nights = (check_out - check_in).days
        except:
            nights = 1
        
        # Base hotel data
        hotels_by_area = {
            "west yellowstone": [
                {
                    "name": "Explorer Cabins at Yellowstone",
                    "address": "250 S Canyon St, West Yellowstone, MT 59758",
                    "price_per_night": 189.99,
                    "rating": 4.6,
                    "amenities": ["Free WiFi", "Parking", "Pet Friendly", "Kitchenette"],
                    "description": "Cozy cabins near the west entrance of Yellowstone National Park",
                    "availability": True,
                },
                {
                    "name": "Kelly Inn West Yellowstone",
                    "address": "104 S Canyon St, West Yellowstone, MT 59758",
                    "price_per_night": 159.99,
                    "rating": 4.3,
                    "amenities": ["Free WiFi", "Breakfast included", "Pool", "Parking"],
                    "description": "Family-friendly hotel with indoor pool, just blocks from the park entrance",
                    "availability": True,
                },
                {
                    "name": "Yellowstone Park Hotel",
                    "address": "201 Grizzly Ave, West Yellowstone, MT 59758",
                    "price_per_night": 179.99,
                    "rating": 4.4,
                    "amenities": ["Free WiFi", "Fitness center", "Breakfast included"],
                    "description": "Modern hotel with convenient access to Yellowstone National Park",
                    "availability": False,
                },
                {
                    "name": "Gray Wolf Inn & Suites",
                    "address": "250 S Canyon St, West Yellowstone, MT 59758",
                    "price_per_night": 169.99,
                    "rating": 4.2,
                    "amenities": ["Free WiFi", "Indoor Pool", "Hot Tub", "Breakfast included"],
                    "description": "Comfortable accommodations near the west entrance with indoor pool",
                    "availability": True,
                },
            ],
            "gardiner": [
                {
                    "name": "Yellowstone Gateway Inn",
                    "address": "103 Bigelow Ln, Gardiner, MT 59030",
                    "price_per_night": 149.99,
                    "rating": 4.7,
                    "amenities": ["Free WiFi", "Kitchen", "Parking", "Air conditioning"],
                    "description": "Apartment-style accommodations near the north entrance of Yellowstone",
                    "availability": True,
                },
                {
                    "name": "Yellowstone Basin Inn",
                    "address": "4 Jardine Rd, Gardiner, MT 59030",
                    "price_per_night": 179.99,
                    "rating": 4.8,
                    "amenities": ["Free WiFi", "Mountain view", "Breakfast included", "Parking"],
                    "description": "Boutique hotel with panoramic mountain views and gourmet breakfast",
                    "availability": True,
                },
                {
                    "name": "Absaroka Lodge",
                    "address": "310 Scott St W, Gardiner, MT 59030",
                    "price_per_night": 139.99,
                    "rating": 4.1,
                    "amenities": ["Free WiFi", "Parking", "River view"],
                    "description": "Rustic lodge with views of the Yellowstone River",
                    "availability": True,
                },
            ],
            "cody": [
                {
                    "name": "Buffalo Bill Village",
                    "address": "1701 Sheridan Ave, Cody, WY 82414",
                    "price_per_night": 129.99,
                    "rating": 4.0,
                    "amenities": ["Free WiFi", "Pool", "Restaurant", "Parking"],
                    "description": "Cabin-style accommodations in downtown Cody",
                    "availability": True,
                },
                {
                    "name": "Cody Legacy Inn & Suites",
                    "address": "1801 Mountain View Dr, Cody, WY 82414",
                    "price_per_night": 119.99,
                    "rating": 4.2,
                    "amenities": ["Free WiFi", "Breakfast included", "Fitness center", "Pet friendly"],
                    "description": "Comfortable hotel with easy access to Yellowstone",
                    "availability": True,
                },
                {
                    "name": "The Irma Hotel",
                    "address": "1192 Sheridan Ave, Cody, WY 82414",
                    "price_per_night": 149.99,
                    "rating": 4.2,
                    "amenities": ["Free WiFi", "Restaurant", "Bar", "Historic property"],
                    "description": "Historic hotel built by Buffalo Bill Cody himself in 1902",
                    "availability": False,
                },
            ],
            "jackson": [
                {
                    "name": "The Lexington at Jackson Hole",
                    "address": "285 N Cache St, Jackson, WY 83001",
                    "price_per_night": 229.99,
                    "rating": 4.5,
                    "amenities": ["Free WiFi", "Breakfast included", "Pool", "Hot tub"],
                    "description": "Hotel & Suites with modern amenities in downtown Jackson",
                    "availability": True,
                },
                {
                    "name": "Wyoming Inn of Jackson Hole",
                    "address": "930 W Broadway, Jackson, WY 83001",
                    "price_per_night": 259.99,
                    "rating": 4.7,
                    "amenities": ["Free WiFi", "Restaurant", "Fitness center", "Luxury bedding"],
                    "description": "Upscale hotel with western charm and modern amenities",
                    "availability": False,
                },
                {
                    "name": "Elk Country Inn",
                    "address": "480 W Pearl Ave, Jackson, WY 83001",
                    "price_per_night": 189.99,
                    "rating": 4.3,
                    "amenities": ["Free WiFi", "Breakfast included", "Parking", "Ski storage"],
                    "description": "Comfortable hotel within walking distance of Jackson Town Square",
                    "availability": True,
                },
            ],
            "yellowstone national park": [
                {
                    "name": "Old Faithful Inn",
                    "address": "Old Faithful Inn Rd, Yellowstone National Park, WY 82190",
                    "price_per_night": 219.99,
                    "rating": 4.6,
                    "amenities": ["Restaurant", "Historic property", "Located in park"],
                    "description": "Historic log hotel adjacent to Old Faithful geyser",
                    "availability": False,
                },
                {
                    "name": "Lake Yellowstone Hotel",
                    "address": "235 Yellowstone Lake Rd, Yellowstone National Park, WY 82190",
                    "price_per_night": 259.99,
                    "rating": 4.5,
                    "amenities": ["Restaurant", "Historic property", "Located in park", "Lake view"],
                    "description": "Historic Colonial Revival hotel with stunning lake views",
                    "availability": True,
                },
                {
                    "name": "Canyon Lodge",
                    "address": "Canyon Village, Yellowstone National Park, WY 82190",
                    "price_per_night": 189.99,
                    "rating": 4.0,
                    "amenities": ["Restaurant", "Located in park", "Modern facilities"],
                    "description": "Recently renovated lodging near the Grand Canyon of Yellowstone",
                    "availability": True,
                },
                {
                    "name": "Mammoth Hot Springs Hotel",
                    "address": "Mammoth Hot Springs, Yellowstone National Park, WY 82190",
                    "price_per_night": 199.99,
                    "rating": 4.2,
                    "amenities": ["Restaurant", "Historic area", "Located in park"],
                    "description": "Hotel and cabins located in the historic Fort Yellowstone area",
                    "availability": True,
                },
            ]
        }
        
        # Match location (case insensitive)
        search_location = location.lower()
        matching_hotels = []
        
        # Direct location match
        for loc, hotels in hotels_by_area.items():
            if loc in search_location or search_location in loc:
                matching_hotels.extend(hotels)
                
        # If no matches and it might be "Yellowstone area", use all hotels
        if not matching_hotels and "yellowstone" in search_location:
            for hotels in hotels_by_area.values():
                matching_hotels.extend(hotels)
        
        # Filter by max price
        if max_price:
            matching_hotels = [h for h in matching_hotels if h["price_per_night"] <= max_price]
            
        # Filter by amenities
        if amenities:
            amenities_lower = [a.lower() for a in amenities]
            filtered_hotels = []
            for hotel in matching_hotels:
                hotel_amenities_lower = [a.lower() for a in hotel["amenities"]]
                if all(a in hotel_amenities_lower for a in amenities_lower):
                    filtered_hotels.append(hotel)
            matching_hotels = filtered_hotels
            
        # Calculate total prices
        for hotel in matching_hotels:
            hotel["total_price"] = round(hotel["price_per_night"] * nights, 2)
            
        # Limit to available hotels
        available_hotels = [h for h in matching_hotels if h["availability"]]
        
        # If we have too few, include some that are "magically" available now
        if len(available_hotels) < 3 and matching_hotels:
            for hotel in matching_hotels:
                if not hotel["availability"]:
                    hotel["availability"] = True
                    hotel["note"] = "Limited availability - book soon!"
                    available_hotels.append(hotel)
                if len(available_hotels) >= 3:
                    break
        
        # Return formatted results
        return {
            "location": location,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "nights": nights,
            "hotels": available_hotels,
            "total_options": len(available_hotels)
        }
    
    def get_resource_group_name(self) -> str:
        """Retrieve the name of the resource group."""
        return "AgenticTravel"
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import List, Optional
import requests
import os

class RestaurantRequest(BaseModel):
    location: str = Field(..., description="Location to search for restaurants")
    cuisine_preferences: Optional[List[str]] = Field(default=None, description="List of preferred cuisines")
    price_level: Optional[str] = Field(default=None, description="Price level (budget, moderate, expensive)")
    meal_type: Optional[str] = Field(default=None, description="Type of meal (breakfast, lunch, dinner)")

class RestaurantTool(BaseTool):
    name = "restaurant_finder"
    description = "Find restaurants along the route to Yellowstone National Park"
    args_schema = RestaurantRequest
    
    def _run(self, location: str, cuisine_preferences: Optional[List[str]] = None, 
             price_level: Optional[str] = None, meal_type: Optional[str] = None):
        """Find restaurants matching the specified criteria"""
        try:
            # In production, you would use a real restaurant API like Google Places, Yelp, etc.
            api_key = os.getenv("RESTAURANT_API_KEY")
            
            # Simulate restaurant search
            restaurants = self._simulate_restaurant_data(location, cuisine_preferences, price_level, meal_type)
            
            return {
                "location": location,
                "restaurants": restaurants,
                "source": "Simulated Restaurant Database"
            }
        except Exception as e:
            return f"Error finding restaurants: {str(e)}"
    
    def _simulate_restaurant_data(self, location, cuisine_preferences, price_level, meal_type):
        """Simulate restaurant data for demo purposes"""
        # Restaurant database by location (simplified)
        restaurant_db = {
            "West Yellowstone": [
                {"name": "Madison Crossing Lounge", "cuisine": "American", "price_level": "moderate", 
                 "rating": 4.3, "address": "121 Madison Ave", "phone": "406-555-1234"},
                {"name": "Cafe Madriz", "cuisine": "Spanish", "price_level": "moderate", 
                 "rating": 4.7, "address": "311 Canyon St", "phone": "406-555-2345"},
                {"name": "Wild West Pizzeria", "cuisine": "Italian", "price_level": "budget", 
                 "rating": 4.1, "address": "14 Madison Ave", "phone": "406-555-3456"}
            ],
            "Gardiner": [
                {"name": "Wonderland Cafe", "cuisine": "American", "price_level": "moderate", 
                 "rating": 4.4, "address": "206 Main St", "phone": "406-555-4567"},
                {"name": "Yellowstone Pizza Company", "cuisine": "Italian", "price_level": "budget", 
                 "rating": 4.0, "address": "804 Scott St", "phone": "406-555-5678"}
            ],
            "Cody": [
                {"name": "Proud Cut Saloon", "cuisine": "American", "price_level": "moderate", 
                 "rating": 4.2, "address": "1227 Sheridan Ave", "phone": "307-555-6789"},
                {"name": "Millstone Pizza Company", "cuisine": "Italian", "price_level": "budget", 
                 "rating": 4.5, "address": "1057 Sheridan Ave", "phone": "307-555-7890"}
            ],
            "Jackson": [
                {"name": "Gun Barrel Steak House", "cuisine": "American", "price_level": "expensive", 
                 "rating": 4.6, "address": "862 W Broadway", "phone": "307-555-8901"},
                {"name": "Snake River Grill", "cuisine": "American", "price_level": "expensive", 
                 "rating": 4.8, "address": "84 E Broadway", "phone": "307-555-9012"},
                {"name": "Hand Fire Pizza", "cuisine": "Italian", "price_level": "moderate", 
                 "rating": 4.5, "address": "120 W Broadway", "phone": "307-555-0123"}
            ],
            # Add more locations as needed
        }
        
        # Generate default locations for unknown places
        if location not in restaurant_db:
            import random
            restaurant_db[location] = [
                {"name": f"{location} Diner", "cuisine": "American", "price_level": "budget", 
                 "rating": round(random.uniform(3.5, 4.5), 1), "address": f"123 Main St, {location}", "phone": "555-123-4567"},
                {"name": f"{location} Grill", "cuisine": "American", "price_level": "moderate", 
                 "rating": round(random.uniform(3.8, 4.7), 1), "address": f"456 Oak Ave, {location}", "phone": "555-234-5678"},
                {"name": f"Pasta Palace", "cuisine": "Italian", "price_level": "moderate", 
                 "rating": round(random.uniform(3.7, 4.6), 1), "address": f"789 Elm St, {location}", "phone": "555-345-6789"}
            ]
        
        # Filter by cuisine if specified
        results = restaurant_db[location]
        if cuisine_preferences:
            results = [r for r in results if r["cuisine"] in cuisine_preferences]
        
        # Filter by price level if specified
        if price_level:
            results = [r for r in results if r["price_level"] == price_level]
        
        # Add reservation availability
        import random
        for restaurant in results:
            restaurant["accepts_reservations"] = random.choice([True, True, True, False])
            if restaurant["accepts_reservations"]:
                restaurant["available_times"] = ["5:00 PM", "6:30 PM", "8:00 PM"]
        
        return results
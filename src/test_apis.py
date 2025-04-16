from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any, Optional

app = FastAPI(
    title="Yellowstone Trip Planner Test APIs",
    description="Test APIs for the Yellowstone Trip Planner application",
    version="1.0.0"
)

# Mock data stores
weather_data = {}
hotel_data = {}
restaurant_data = {}
reservation_data = {}

# Predefined routes with waypoints and recommended hotels
PREDEFINED_ROUTES = {
    "san_jose": {
        "name": "San Jose to Yellowstone",
        "origin": "San Jose, CA",
        "destination": "Yellowstone National Park",
        "waypoints": [
            {"location": "Reno, NV", "distance": 260, "duration": 4.5},
            {"location": "Salt Lake City, UT", "distance": 520, "duration": 7.5},
            {"location": "Idaho Falls, ID", "distance": 210, "duration": 3.5}
        ],
        "total_distance": 990,
        "total_duration": 15.5,
        "recommended_hotels": [
            {"location": "Reno", "area": "stopover"},
            {"location": "Salt Lake City", "area": "stopover"},
            {"location": "West Yellowstone", "area": "destination"}
        ]
    },
    "redmond": {
        "name": "Redmond to Yellowstone",
        "origin": "Redmond, WA",
        "destination": "Yellowstone National Park",
        "waypoints": [
            {"location": "Spokane, WA", "distance": 280, "duration": 4.0},
            {"location": "Missoula, MT", "distance": 200, "duration": 3.0},
            {"location": "Bozeman, MT", "distance": 203, "duration": 3.0}
        ],
        "total_distance": 683,
        "total_duration": 10.0,
        "recommended_hotels": [
            {"location": "Spokane", "area": "stopover"},
            {"location": "Bozeman", "area": "stopover"},
            {"location": "Gardiner", "area": "destination"}
        ]
    },
    "new_york": {
        "name": "New York to Yellowstone",
        "origin": "New York, NY",
        "destination": "Yellowstone National Park",
        "waypoints": [
            {"location": "Chicago, IL", "distance": 790, "duration": 12.0},
            {"location": "Sioux Falls, SD", "distance": 580, "duration": 8.5},
            {"location": "Billings, MT", "distance": 450, "duration": 6.5}
        ],
        "total_distance": 1820,
        "total_duration": 27.0,
        "recommended_hotels": [
            {"location": "Chicago", "area": "stopover"},
            {"location": "Sioux Falls", "area": "stopover"},
            {"location": "Billings", "area": "stopover"},
            {"location": "Cody", "area": "destination"}
        ]
    }
}

@app.get("/")
async def root():
    """Root endpoint that provides API information"""
    return {
        "name": "Yellowstone Trip Planner Test APIs",
        "version": "1.0.0",
        "description": "Test APIs for simulating various services",
        "endpoints": {
            "weather": "/weather/{location}",
            "hotels": {
                "search": "/hotels/search",
                "reserve": "/hotels/reserve"
            },
            "restaurants": {
                "search": "/restaurants/search",
                "reserve": "/restaurants/reserve"
            },
            "routes": "/routes/plan"
        },
        "docs": "/docs",
        "openapi": "/openapi.json"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/weather/{location}")
async def get_weather(location: str, start_date: str, end_date: str):
    """Mock weather API endpoint"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        weather_options = [
            {"condition": "Sunny", "description": "Clear sky", "high_temp": 75, "low_temp": 45, "precipitation": 0},
            {"condition": "Partly Cloudy", "description": "Some clouds", "high_temp": 70, "low_temp": 42, "precipitation": 10},
            {"condition": "Thunderstorm", "description": "Scattered storms", "high_temp": 65, "low_temp": 40, "precipitation": 70},
            {"condition": "Rain", "description": "Light rain", "high_temp": 60, "low_temp": 38, "precipitation": 80}
        ]
        
        forecasts = []
        current_date = start
        while current_date <= end:
            weather = random.choice(weather_options)
            # Add some variation
            weather["high_temp"] += random.randint(-5, 5)
            weather["low_temp"] += random.randint(-3, 3)
            
            forecasts.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "condition": weather["condition"],
                "description": weather["description"],
                "high_temp_f": weather["high_temp"],
                "low_temp_f": weather["low_temp"],
                "precipitation_chance": weather["precipitation"]
            })
            current_date += timedelta(days=1)
            
        return {"location": location, "forecasts": forecasts}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

@app.get("/hotels/search")
async def search_hotels(location: str, check_in: str, check_out: str, 
                       max_price: Optional[float] = None, amenities: Optional[List[str]] = None):
    """Mock hotel search API endpoint"""
    hotels = [
        {
            "name": "Old Faithful Inn",
            "location": "Yellowstone National Park",
            "price": 219.99,
            "rating": 4.6,
            "amenities": ["Restaurant", "Historic property", "Located in park"],
            "availability": True
        },
        {
            "name": "Lake Yellowstone Hotel",
            "location": "Yellowstone National Park",
            "price": 259.99,
            "rating": 4.5,
            "amenities": ["Restaurant", "Lake view", "Located in park"],
            "availability": True
        },
        {
            "name": "Explorer Cabins",
            "location": "West Yellowstone",
            "price": 189.99,
            "rating": 4.4,
            "amenities": ["Kitchenette", "Free WiFi", "Parking"],
            "availability": True
        }
    ]
    
    # Filter by price if specified
    if max_price:
        hotels = [h for h in hotels if h["price"] <= max_price]
    
    # Filter by amenities if specified
    if amenities:
        filtered = []
        for hotel in hotels:
            if all(amenity in hotel["amenities"] for amenity in amenities):
                filtered.append(hotel)
        hotels = filtered
    
    return {"results": hotels}

@app.post("/hotels/reserve")
async def reserve_hotel(hotel_name: str, check_in: str, check_out: str, guests: int):
    """Mock hotel reservation API endpoint"""
    confirmation = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))
    success = random.random() < 0.9  # 90% success rate
    
    if success:
        return {
            "status": "confirmed",
            "confirmation_code": confirmation,
            "hotel": hotel_name,
            "check_in": check_in,
            "check_out": check_out,
            "guests": guests
        }
    else:
        raise HTTPException(status_code=400, detail="Unable to complete reservation")

@app.get("/restaurants/search")
async def search_restaurants(location: str, cuisine: Optional[str] = None, price_level: str = "moderate"):
    """Mock restaurant search API endpoint"""
    restaurants = [
        {
            "name": "Old Faithful Inn Dining Room",
            "location": "Old Faithful, Yellowstone",
            "cuisine": "American",
            "price_level": "moderate",
            "rating": 4.3,
            "availability": True
        },
        {
            "name": "Lake Hotel Diner",
            "location": "Lake Village, Yellowstone",
            "cuisine": "American",
            "price_level": "budget",
            "rating": 4.0,
            "availability": True
        },
        {
            "name": "Madison Crossing Lounge",
            "location": "West Yellowstone",
            "cuisine": "American",
            "price_level": "moderate",
            "rating": 4.5,
            "availability": True
        }
    ]
    
    # Filter by cuisine if specified
    if cuisine:
        restaurants = [r for r in restaurants if r["cuisine"].lower() == cuisine.lower()]
    
    # Filter by price level
    restaurants = [r for r in restaurants if r["price_level"] == price_level]
    
    return {"results": restaurants}

@app.post("/restaurants/reserve")
async def reserve_restaurant(restaurant_name: str, date: str, time: str, party_size: int):
    """Mock restaurant reservation API endpoint"""
    confirmation = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
    success = random.random() < 0.85  # 85% success rate
    
    if success:
        return {
            "status": "confirmed",
            "confirmation_code": confirmation,
            "restaurant": restaurant_name,
            "date": date,
            "time": time,
            "party_size": party_size
        }
    else:
        raise HTTPException(status_code=400, detail="No availability for selected time")

@app.get("/routes/plan")
async def plan_route(origin: str, destination: str, waypoints: Optional[List[str]] = None):
    """Mock route planning API endpoint"""
    def calculate_mock_distance(point1: str, point2: str) -> float:
        """Generate a reasonable mock distance between two points"""
        # In a real implementation, this would use actual coordinates
        return random.uniform(20, 200)
    
    route_segments = []
    points = [origin] + (waypoints or []) + [destination]
    
    total_distance = 0
    total_duration = 0
    
    for i in range(len(points) - 1):
        distance = calculate_mock_distance(points[i], points[i+1])
        duration = distance / 65 * 60  # Assume average speed of 65 mph
        
        route_segments.append({
            "from": points[i],
            "to": points[i+1],
            "distance_miles": round(distance, 1),
            "duration_minutes": round(duration),
            "road_names": ["US-191", "Grand Loop Road"] if "Yellowstone" in points[i+1] else ["I-90", "US-191"]
        })
        
        total_distance += distance
        total_duration += duration
    
    return {
        "segments": route_segments,
        "total_distance_miles": round(total_distance, 1),
        "total_duration_minutes": round(total_duration),
        "total_duration_hours": round(total_duration / 60, 1)
    }

@app.get("/routes/available")
async def get_available_routes():
    """Get list of predefined routes to Yellowstone"""
    return {
        "routes": [
            {
                "id": route_id,
                "name": route_data["name"],
                "origin": route_data["origin"],
                "total_distance": route_data["total_distance"],
                "total_duration": route_data["total_duration"]
            }
            for route_id, route_data in PREDEFINED_ROUTES.items()
        ]
    }

@app.get("/routes/{route_id}/details")
async def get_route_details(route_id: str):
    """Get detailed information about a specific route"""
    if route_id not in PREDEFINED_ROUTES:
        raise HTTPException(status_code=404, detail="Route not found")
    return PREDEFINED_ROUTES[route_id]

@app.get("/hotels/recommended")
async def get_recommended_hotels(route_id: str, check_in: str, check_out: str, guests: int = 2):
    """Get hotel recommendations based on the selected route"""
    if route_id not in PREDEFINED_ROUTES:
        raise HTTPException(status_code=404, detail="Route not found")
    
    route = PREDEFINED_ROUTES[route_id]
    hotels = []
    
    for hotel_area in route["recommended_hotels"]:
        area_hotels = [
            {
                "name": f"{hotel['name']} ({hotel_area['location']})",
                "location": hotel_area["location"],
                "area_type": hotel_area["area"],
                "price": hotel["price"],
                "rating": hotel["rating"],
                "amenities": hotel["amenities"],
                "availability": hotel["availability"]
            }
            for hotel in await search_hotels(
                hotel_area["location"], 
                check_in, 
                check_out
            )["results"]
        ]
        hotels.extend(area_hotels)
    
    return {"results": hotels}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
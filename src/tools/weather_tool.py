from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import requests
from datetime import datetime, timedelta
import os
import json

class WeatherRequest(BaseModel):
    location: str = Field(..., description="Location for weather forecast (e.g., 'Yellowstone National Park')")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")

class WeatherTool(BaseTool):
    name = "weather_service"
    description = "Get weather forecasts for Yellowstone National Park area for specific dates"
    args_schema = WeatherRequest
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("WEATHER_API_KEY")
        self.api_host = "open-weather13.p.rapidapi.com"
        self.location_coords = {
            "Yellowstone National Park": {"lat": 44.4280, "lon": -110.5885},
            "West Yellowstone": {"lat": 44.6613, "lon": -111.1043},
            "Old Faithful": {"lat": 44.4605, "lon": -110.8281},
            "Grand Canyon of the Yellowstone": {"lat": 44.7179, "lon": -110.4987},
            "Mammoth Hot Springs": {"lat": 44.9769, "lon": -110.7033},
            "Jackson": {"lat": 43.4799, "lon": -110.7624},
            "Cody": {"lat": 44.5263, "lon": -109.0565},
            "Gardiner": {"lat": 45.0324, "lon": -110.7054},
            "Bozeman": {"lat": 45.6770, "lon": -111.0429},
            "Salt Lake City": {"lat": 40.7608, "lon": -111.8910},
            "Denver": {"lat": 39.7392, "lon": -104.9903},
            "Boise": {"lat": 43.6150, "lon": -116.2023},
            "Seattle": {"lat": 47.6062, "lon": -122.3321}
        }
    
    def _run(self, location: str, start_date: str, end_date: str):
        """Get weather forecasts for the specified location and date range"""
        try:
            # Check if we have the coordinates for the location
            if location in self.location_coords:
                coords = self.location_coords[location]
                weather_data = self._fetch_weather_data(coords["lat"], coords["lon"])
                
                # Process the API response
                processed_data = self._process_weather_data(weather_data, start_date, end_date)
                
                return {
                    "location": location,
                    "forecasts": processed_data,
                    "source": "Open Weather API"
                }
            else:
                # For locations we don't have coordinates for, use simulated data
                print(f"No coordinates found for {location}, using simulated weather data.")
                weather_data = self._simulate_weather_data(start_date, end_date)
                
                return {
                    "location": location,
                    "forecasts": weather_data,
                    "source": "Simulated Weather Service"
                }
        except Exception as e:
            print(f"Error fetching weather data: {str(e)}")
            # Fall back to simulated data
            weather_data = self._simulate_weather_data(start_date, end_date)
            
            return {
                "location": location,
                "forecasts": weather_data,
                "source": "Simulated Weather Service (fallback)"
            }
    
    def _fetch_weather_data(self, lat, lon):
        """Fetch weather data from the Open Weather API"""
        url = f"https://open-weather13.p.rapidapi.com/city/latlon/{lat}/{lon}"
        
        headers = {
            "x-rapidapi-host": self.api_host,
            "x-rapidapi-key": self.api_key
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
    
    def _process_weather_data(self, api_response, start_date, end_date):
        """Process the API response into our standard forecast format"""
        # This is a simplification since the actual API might return different data
        # We'll extract what we can from the current conditions
        
        # Parse the dates
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        forecasts = []
        current_date = start
        
        # The free tier API might only provide current weather
        # So we'll use the current data and add variation for future dates
        if "main" in api_response and "weather" in api_response:
            base_temp = api_response["main"]["temp"]
            base_condition = api_response["weather"][0]["main"]
            base_description = api_response["weather"][0]["description"]
            
            import random
            while current_date <= end:
                # Add some variation for future dates
                high_temp = round((base_temp * 9/5) - 459.67) + random.randint(-5, 5)  # Convert from Kelvin to Fahrenheit
                low_temp = high_temp - random.randint(20, 30)  # Typical day/night difference
                
                forecasts.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "condition": base_condition,
                    "description": base_description,
                    "high_temp_f": high_temp,
                    "low_temp_f": low_temp,
                    "precipitation_chance": random.randint(0, 50) if "Rain" in base_condition else random.randint(0, 20)
                })
                
                current_date += timedelta(days=1)
        else:
            # Fall back to simulated data if API response is not as expected
            forecasts = self._simulate_weather_data(start_date, end_date)
            
        return forecasts
    
    def _simulate_weather_data(self, start_date, end_date):
        """Simulate weather data for demo purposes"""
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        forecasts = []
        current_date = start
        
        # Yellowstone typical summer weather patterns
        weather_options = [
            {"condition": "Sunny", "description": "Clear sky", "high_temp": 75, "low_temp": 45, "precipitation": 0},
            {"condition": "Clouds", "description": "Partly cloudy", "high_temp": 70, "low_temp": 42, "precipitation": 10},
            {"condition": "Thunderstorm", "description": "Thunderstorms", "high_temp": 65, "low_temp": 40, "precipitation": 70},
            {"condition": "Clear", "description": "Clear sky", "high_temp": 72, "low_temp": 44, "precipitation": 0},
            {"condition": "Rain", "description": "Light rain", "high_temp": 60, "low_temp": 38, "precipitation": 80}
        ]
        
        import random
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
            
        return forecasts
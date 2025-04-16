from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import requests
from datetime import datetime, timedelta
import os
import json
from typing import Dict, Any

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
        self.api_url = "http://localhost:8000"  # Test API endpoint
    
    def _run(self, location: str, start_date: str, end_date: str):
        """Get weather forecasts for the specified location and date range"""
        try:
            response = requests.get(
                f"{self.api_url}/weather/{location}",
                params={
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Warning: Weather API returned status code {response.status_code}")
                return self._simulate_weather_data(start_date, end_date)
                
        except Exception as e:
            print(f"Warning: Error calling weather API: {e}")
            return self._simulate_weather_data(start_date, end_date)
    
    def _simulate_weather_data(self, start_date: str, end_date: str):
        """Fallback to simulated data if API is unavailable"""
        try:
            response = requests.get(
                f"{self.api_url}/weather/Yellowstone",
                params={
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            return response.json()
        except:
            # Final fallback with basic mock data
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            forecasts = []
            current_date = start
            
            while current_date <= end:
                forecasts.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "condition": "Sunny",
                    "description": "Clear sky",
                    "high_temp_f": 75,
                    "low_temp_f": 45,
                    "precipitation_chance": 0
                })
                current_date += timedelta(days=1)
            
            return {
                "location": "Yellowstone National Park",
                "forecasts": forecasts
            }
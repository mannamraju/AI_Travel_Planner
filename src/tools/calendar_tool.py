from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
import random

class CalendarRequest(BaseModel):
    travel_window_start: str = Field(..., description="Start of available travel window in YYYY-MM-DD format")
    travel_window_end: str = Field(..., description="End of available travel window in YYYY-MM-DD format")
    trip_duration_days: int = Field(..., description="Desired trip duration in days")
    preferred_day_of_week_start: Optional[str] = Field(default=None, description="Preferred day of week to start trip")

class CalendarOptimizerTool(BaseTool):
    name = "calendar_optimizer"
    description = "Find optimal travel dates for Yellowstone within a specified window"
    args_schema = CalendarRequest
    
    def _run(self, travel_window_start: str, travel_window_end: str, trip_duration_days: int,
             preferred_day_of_week_start: Optional[str] = None):
        """Find optimal travel dates based on weather, crowd levels, and other factors"""
        try:
            start_date = datetime.strptime(travel_window_start, "%Y-%m-%d")
            end_date = datetime.strptime(travel_window_end, "%Y-%m-%d")
            
            # Calculate possible start dates
            possible_dates = []
            current_date = start_date
            
            while current_date <= end_date - timedelta(days=trip_duration_days-1):
                # Filter by preferred day of week if specified
                if preferred_day_of_week_start:
                    day_name = current_date.strftime("%A").lower()
                    if day_name != preferred_day_of_week_start.lower():
                        current_date += timedelta(days=1)
                        continue
                
                trip_end = current_date + timedelta(days=trip_duration_days-1)
                
                # Calculate scores for this date range (weather, crowds, etc.)
                weather_score = self._simulate_weather_score(current_date, trip_end)
                crowd_score = self._simulate_crowd_score(current_date, trip_end)
                wildlife_score = self._simulate_wildlife_score(current_date, trip_end)
                
                total_score = weather_score * 0.4 + crowd_score * 0.4 + wildlife_score * 0.2
                
                possible_dates.append({
                    "start_date": current_date.strftime("%Y-%m-%d"),
                    "end_date": trip_end.strftime("%Y-%m-%d"),
                    "total_score": round(total_score, 2),
                    "weather_score": round(weather_score, 2),
                    "crowd_score": round(crowd_score, 2),
                    "wildlife_score": round(wildlife_score, 2)
                })
                
                current_date += timedelta(days=1)
            
            # Sort by score (highest first)
            possible_dates.sort(key=lambda x: x["total_score"], reverse=True)
            
            # Select top 3 recommendations
            recommendations = possible_dates[:3]
            
            return {
                "recommended_date_ranges": recommendations,
                "reasoning": self._generate_reasoning(recommendations)
            }
            
        except Exception as e:
            return f"Error optimizing travel dates: {str(e)}"
    
    def _simulate_weather_score(self, start_date, end_date):
        """Simulate weather desirability score"""
        # In real app, this would use historical weather data
        
        # Yellowstone weather tends to be best from June-September
        month = start_date.month
        
        if month in [7, 8]:  # July-August
            base_score = random.uniform(0.8, 1.0)
        elif month in [6, 9]:  # June, September
            base_score = random.uniform(0.6, 0.9)
        elif month in [5, 10]:  # May, October
            base_score = random.uniform(0.3, 0.7)
        else:  # Winter months
            base_score = random.uniform(0.1, 0.5)
            
        # Add some randomness
        return min(1.0, base_score + random.uniform(-0.1, 0.1))
    
    def _simulate_crowd_score(self, start_date, end_date):
        """Simulate crowd level score (higher = less crowded = better)"""
        # In real app, this would use historical visitation data
        
        month = start_date.month
        day_of_week = start_date.weekday()
        
        # Summer months are most crowded
        if month in [7, 8]:  # Peak season
            base_score = random.uniform(0.2, 0.5)
        elif month in [6, 9]:  # Shoulder season
            base_score = random.uniform(0.5, 0.8)
        else:  # Off season
            base_score = random.uniform(0.7, 1.0)
            
        # Weekdays are less crowded than weekends
        if day_of_week >= 5:  # Weekend
            base_score -= 0.1
            
        # US holidays are more crowded
        # (simplified - would check actual holiday dates in production)
        if ((month == 5 and start_date.day >= 25) or    # Memorial Day
            (month == 7 and start_date.day >= 1 and start_date.day <= 7) or    # July 4th
            (month == 9 and start_date.day <= 7)):    # Labor Day
            base_score -= 0.2
            
        return max(0.1, min(1.0, base_score + random.uniform(-0.1, 0.1)))
    
    def _simulate_wildlife_score(self, start_date, end_date):
        """Simulate wildlife viewing opportunity score"""
        # In real app, this would use wildlife activity data
        
        month = start_date.month
        
        # Spring and fall are often best for wildlife
        if month in [5, 9, 10]:  # Spring and fall
            base_score = random.uniform(0.7, 1.0)
        elif month in [6, 7, 8]:  # Summer
            base_score = random.uniform(0.5, 0.8)
        else:  # Winter
            base_score = random.uniform(0.3, 0.7)
            
        return min(1.0, base_score + random.uniform(-0.1, 0.1))
    
    def _generate_reasoning(self, recommendations):
        """Generate explanation for date recommendations"""
        # This would be more detailed in production
        if not recommendations:
            return "No suitable dates found within your travel window."
            
        top_choice = recommendations[0]
        
        # Generate reasoning based on scores
        reasons = []
        
        if top_choice["weather_score"] > 0.7:
            reasons.append("excellent weather conditions")
        elif top_choice["weather_score"] > 0.5:
            reasons.append("good weather conditions")
        else:
            reasons.append("acceptable weather conditions")
            
        if top_choice["crowd_score"] > 0.7:
            reasons.append("low crowd levels")
        elif top_choice["crowd_score"] > 0.5:
            reasons.append("moderate crowd levels")
        else:
            reasons.append("higher crowd levels")
            
        if top_choice["wildlife_score"] > 0.7:
            reasons.append("excellent wildlife viewing opportunities")
        elif top_choice["wildlife_score"] > 0.5:
            reasons.append("good wildlife viewing opportunities")
            
        month_name = datetime.strptime(top_choice["start_date"], "%Y-%m-%d").strftime("%B")
        
        return f"The recommended dates in {month_name} offer {', '.join(reasons[:-1])} and {reasons[-1]}. " + \
               f"This combination provides the best overall experience based on your trip parameters."
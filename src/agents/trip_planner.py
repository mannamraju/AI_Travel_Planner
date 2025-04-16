from typing import Dict, Any
from datetime import datetime
import os
import asyncio

from agents.orchestrator_agent import OrchestratorAgent

class YellowstoneTripPlanner:
    """
    Main entry point for the Yellowstone Trip Planner application.
    Uses an orchestrator pattern to coordinate specialized agents.
    """
    
    def __init__(self):
        # Initialize the orchestrator agent that will coordinate specialized agents
        self.orchestrator = OrchestratorAgent()
        
    async def plan_trip(self,
                       starting_location: str,
                       travel_window_start: datetime,
                       travel_window_end: datetime,
                       trip_duration_days: int,
                       preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive trip plan for Yellowstone National Park.
        
        This method delegates planning to the orchestrator agent, which coordinates:
        - Optimal date selection (calendar_agent)
        - Weather forecasting (weather_agent)
        - Route planning (route_agent) 
        - Restaurant recommendations (dining_agent)
        
        The orchestrator ensures these agents work in parallel where possible,
        while respecting dependencies (e.g., restaurant recommendations depend on routes).
        
        Args:
            starting_location: Where the trip will start from
            travel_window_start: Earliest possible departure date
            travel_window_end: Latest possible return date
            trip_duration_days: How many days the trip should last
            preferences: Optional dict with dining and activity preferences
            
        Returns:
            A comprehensive trip plan with dates, routes, and recommendations
        """
        
        # Delegate to the orchestrator agent
        trip_plan = await self.orchestrator.plan_trip(
            starting_location=starting_location,
            travel_window_start=travel_window_start,
            travel_window_end=travel_window_end,
            trip_duration_days=trip_duration_days,
            preferences=preferences
        )
        
        return trip_plan
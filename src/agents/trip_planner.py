from typing import Dict, Any
from datetime import datetime

from .orchestrator_agent import OrchestratorAgent

class YellowstoneTripPlanner:
    """
    Main entry point for the Yellowstone Trip Planner application.
    Uses an orchestrator pattern to coordinate specialized agents.
    """
    
    def __init__(self):
        self.orchestrator = OrchestratorAgent()
    
    async def plan_trip(self,
                       starting_location: str,
                       travel_window_start: datetime,
                       travel_window_end: datetime,
                       trip_duration_days: int,
                       preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Plan a comprehensive Yellowstone trip by coordinating multiple specialized agents
        """
        return await self.orchestrator.plan_trip(
            starting_location=starting_location,
            travel_window_start=travel_window_start,
            travel_window_end=travel_window_end,
            trip_duration_days=trip_duration_days,
            preferences=preferences
        )
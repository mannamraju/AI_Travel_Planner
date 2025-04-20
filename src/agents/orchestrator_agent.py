from typing import List, Dict, Any, Optional
import os
from datetime import datetime, timedelta
import asyncio
import json
from pydantic import BaseModel, Field

from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from .weather_agent import WeatherAgent
from .route_agent import RouteAgent
from .dining_agent import DiningAgent
from .calendar_agent import CalendarAgent
from ..tools.bing_search_tool import BingSearchTool
from ..tools.base_tool import CustomBaseTool

class CalendarToolInput(BaseModel):
    travel_window_start: str = Field(..., description="Start of available travel window in YYYY-MM-DD format")
    travel_window_end: str = Field(..., description="End of available travel window in YYYY-MM-DD format")
    trip_duration_days: int = Field(..., description="Desired trip duration in days")
    preferred_day_of_week_start: Optional[str] = Field(None, description="Preferred day of week to start trip")

class WeatherToolInput(BaseModel):
    location: str = Field(..., description="Location for weather forecast (e.g., 'Yellowstone National Park')")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")

class DiningToolInput(BaseModel):
    locations: List[str] = Field(..., description="List of locations to find restaurants")
    cuisine_preferences: Optional[List[str]] = Field(None, description="Preferred cuisine types")

class OrchestratorAgent:
    """
    Orchestrator agent that coordinates specialized agents for Yellowstone trip planning
    """
    
    def __init__(self):
        # Initialize specialized agents
        self.calendar_agent = CalendarAgent()
        self.weather_agent = WeatherAgent()
        self.route_agent = RouteAgent()
        self.dining_agent = DiningAgent()
        
        # Create the tools that interface with specialized agents
        self.tools = [
            self._create_calendar_tool(),
            self._create_weather_tool(),
            self._create_dining_tool(),
            BingSearchTool()
        ]
        
        # Initialize the LLM
        self.llm = AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            openai_api_version=os.getenv("OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            temperature=0.1
        )
        
        # Create the orchestrator prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert travel planner for Yellowstone National Park trips.
            Your role is to coordinate multiple specialized agents to create comprehensive trip plans.
            
            Break down trip planning into steps:
            1. First, use the calendar agent to find optimal travel dates based on:
                - Weather patterns
                - Crowd levels
                - Wildlife activity
                - Special events
            
            2. Then, simultaneously get weather forecasts for those dates while planning optimal routes.
            
            3. Finally, with route information, coordinate restaurant recommendations along the route.
            
            Before making any decisions, use the Bing search tool to gather up-to-date information about:
            - Current park conditions and seasonality
            - Road openings and closures
            - Special events or considerations
            
            Synthesize all information into a complete trip plan that is logical and cohesive.
            Be thoughtful about coordinating agents to maximize parallelization while ensuring
            that dependencies are respected (e.g., restaurant recommendations need route information).
            """),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
    
    def _create_calendar_tool(self):
        """Create a tool that interfaces with the calendar agent"""
        class CalendarTool(CustomBaseTool):
            name = "calendar_optimizer"
            description = "Find optimal travel dates for Yellowstone within a specified window"
            args_schema = CalendarToolInput
            
            def _run(self, travel_window_start: str, travel_window_end: str, 
                    trip_duration_days: int, preferred_day_of_week_start: Optional[str] = None):
                return asyncio.run(self.calendar_agent_run(travel_window_start, travel_window_end, 
                                                          trip_duration_days, preferred_day_of_week_start))
                
            async def calendar_agent_run(self, travel_window_start, travel_window_end, 
                                         trip_duration_days, preferred_day_of_week_start):
                return await self.calendar_agent.get_optimal_dates(
                    travel_window_start=travel_window_start,
                    travel_window_end=travel_window_end,
                    trip_duration_days=trip_duration_days,
                    preferred_day_of_week_start=preferred_day_of_week_start
                )
        
        tool = CalendarTool()
        tool.calendar_agent = self.calendar_agent
        return tool
    
    def _create_weather_tool(self):
        """Create a tool that interfaces with the weather agent"""
        class WeatherTool(CustomBaseTool):
            name = "weather_forecast"
            description = "Get weather forecasts for a location and date range"
            args_schema = WeatherToolInput
            
            def _run(self, location: str, start_date: str, end_date: str):
                return asyncio.run(self.weather_agent_run(location, start_date, end_date))
                
            async def weather_agent_run(self, location, start_date, end_date):
                return await self.weather_agent.get_forecast(
                    location=location,
                    start_date=start_date,
                    end_date=end_date
                )
        
        tool = WeatherTool()
        tool.weather_agent = self.weather_agent
        return tool
    
    def _create_dining_tool(self):
        """Create a tool that interfaces with the dining agent"""
        class DiningTool(CustomBaseTool):
            name = "restaurant_recommender"
            description = "Get restaurant recommendations for locations along the route"
            args_schema = DiningToolInput
            
            def _run(self, locations: List[str], cuisine_preferences: Optional[List[str]] = None):
                return asyncio.run(self.dining_agent_run(locations, cuisine_preferences))
                
            async def dining_agent_run(self, locations, cuisine_preferences):
                return await self.dining_agent.get_recommendations(
                    locations=locations,
                    cuisine_preferences=cuisine_preferences
                )
        
        tool = DiningTool()
        tool.dining_agent = self.dining_agent
        return tool
    
    async def plan_trip(self, 
                        starting_location: str,
                        travel_window_start: datetime,
                        travel_window_end: datetime,
                        trip_duration_days: int,
                        preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate a comprehensive trip plan using parallel agent execution"""
        
        # Format dates for consistency
        start_str = travel_window_start.strftime("%Y-%m-%d")
        end_str = travel_window_end.strftime("%Y-%m-%d")
        
        # 1. First, find optimal dates using the calendar agent
        dates_response = await self.calendar_agent.get_optimal_dates(
            travel_window_start=start_str,
            travel_window_end=end_str,
            trip_duration_days=trip_duration_days
        )
        
        # Extract the best dates from the response
        best_dates = dates_response["recommended_date_ranges"][0]
        trip_start = best_dates["start_date"]
        trip_end = best_dates["end_date"]
        
        # 2. Parallel: Get weather forecast and plan route
        weather_task = self.weather_agent.get_forecast(
            location="Yellowstone National Park",
            start_date=trip_start,
            end_date=trip_end
        )
        
        route_task = self.route_agent.plan_route(
            starting_location=starting_location,
            duration_days=trip_duration_days,
            preferences=preferences
        )
        
        weather_forecast, route_plan = await asyncio.gather(weather_task, route_task)
        
        # 3. Get restaurant recommendations based on route
        dining_recommendations = await self.dining_agent.get_recommendations(
            locations=route_plan["stops"],
            cuisine_preferences=preferences.get("cuisine_preferences") if preferences else None
        )
        
        # 4. Combine all information into a comprehensive plan
        return {
            "trip_dates": {
                "start": trip_start,
                "end": trip_end,
                "duration_days": trip_duration_days,
                "date_selection_reasoning": dates_response.get("reasoning", "")
            },
            "weather_forecast": weather_forecast,
            "route_plan": route_plan,
            "dining_recommendations": dining_recommendations
        }
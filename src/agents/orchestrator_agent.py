from typing import List, Dict, Any, Optional
import os
from datetime import datetime, timedelta
import asyncio
import json

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import AzureChatOpenAI
from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field

from agents.weather_agent import WeatherAgent
from agents.route_agent import RouteAgent
from agents.dining_agent import DiningAgent
from agents.calendar_agent import CalendarAgent
from tools.bing_search_tool import BingSearchTool

class OrchestratorAgent:
    """
    Orchestrator agent that coordinates specialized agents for Yellowstone trip planning
    """
    
    def __init__(self):
        # Initialize the LLM
        self.llm = AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            openai_api_version=os.getenv("OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            temperature=0.1,
        )
        
        # Initialize specialized agents
        self.calendar_agent = CalendarAgent()
        self.weather_agent = WeatherAgent()
        self.route_agent = RouteAgent()
        self.dining_agent = DiningAgent()
        
        # Create the agent prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert Yellowstone National Park trip planner orchestrator.
            Your role is to coordinate multiple specialized agents to create a comprehensive trip plan.
            
            First, use the calendar agent to determine optimal dates for the trip.
            Then, simultaneously get weather forecasts for those dates while planning optimal routes.
            Finally, with route information, coordinate restaurant recommendations along the route.
            
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
        
        # Create orchestrator tools that call the specialized agents
        self.tools = [
            self._create_calendar_tool(),
            self._create_weather_tool(),
            self._create_route_tool(),
            self._create_dining_tool(),
            BingSearchTool(),
        ]
        
        # Create the agent executor
        self.agent = AgentExecutor(
            agent=self._create_agent(),
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
        )
    
    def _create_agent(self):
        """Create the orchestrator agent using OpenAI functions"""
        def _agent_factory(llm):
            return llm.bind(
                functions=[tool.metadata for tool in self.tools]
            )
        
        return (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_to_openai_function_messages(
                    x["intermediate_steps"]
                ),
            }
            | self.prompt
            | _agent_factory(self.llm)
            | OpenAIFunctionsAgentOutputParser()
        )
    
    def _create_calendar_tool(self):
        """Create a tool that interfaces with the calendar agent"""
        class CalendarToolInput(BaseModel):
            travel_window_start: str = Field(..., description="Start of available travel window in YYYY-MM-DD format")
            travel_window_end: str = Field(..., description="End of available travel window in YYYY-MM-DD format")
            trip_duration_days: int = Field(..., description="Desired trip duration in days")
            preferred_day_of_week_start: Optional[str] = Field(None, description="Preferred day of week to start trip")
            
        class CalendarTool(BaseTool):
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
        class WeatherToolInput(BaseModel):
            location: str = Field(..., description="Location for weather forecast (e.g., 'Yellowstone National Park')")
            start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
            end_date: str = Field(..., description="End date in YYYY-MM-DD format")
            
        class WeatherTool(BaseTool):
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
    
    def _create_route_tool(self):
        """Create a tool that interfaces with the route agent"""
        class RouteToolInput(BaseModel):
            origin: str = Field(..., description="Starting location address or city")
            destination: str = Field(..., description="Destination location (e.g., 'Yellowstone National Park')")
            waypoints: List[str] = Field(default=[], description="Optional locations to visit along the route")
            travel_date: str = Field(..., description="Date of travel in YYYY-MM-DD format")
            
        class RouteTool(BaseTool):
            name = "route_planner"
            description = "Plan driving routes to and around Yellowstone National Park"
            args_schema = RouteToolInput
            
            def _run(self, origin: str, destination: str, waypoints: List[str], travel_date: str):
                return asyncio.run(self.route_agent_run(origin, destination, waypoints, travel_date))
                
            async def route_agent_run(self, origin, destination, waypoints, travel_date):
                return await self.route_agent.plan_route(
                    origin=origin,
                    destination=destination,
                    waypoints=waypoints,
                    travel_date=travel_date
                )
                
        tool = RouteTool()
        tool.route_agent = self.route_agent
        return tool
    
    def _create_dining_tool(self):
        """Create a tool that interfaces with the dining agent"""
        class DiningToolInput(BaseModel):
            locations: List[str] = Field(..., description="List of locations to find restaurants")
            cuisine_preferences: List[str] = Field(default=[], description="Preferred cuisines")
            price_level: str = Field(default="moderate", description="Price level (budget, moderate, expensive)")
            travel_dates: List[str] = Field(..., description="List of dates for the trip in YYYY-MM-DD format")
            
        class DiningTool(BaseTool):
            name = "dining_recommendations"
            description = "Find restaurant recommendations along a route with optional reservation booking"
            args_schema = DiningToolInput
            
            def _run(self, locations: List[str], cuisine_preferences: List[str], 
                    price_level: str, travel_dates: List[str]):
                return asyncio.run(self.dining_agent_run(locations, cuisine_preferences, 
                                                       price_level, travel_dates))
                
            async def dining_agent_run(self, locations, cuisine_preferences, price_level, travel_dates):
                return await self.dining_agent.get_recommendations(
                    locations=locations,
                    cuisine_preferences=cuisine_preferences,
                    price_level=price_level,
                    travel_dates=travel_dates
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
        
        # Default preferences if none provided
        if preferences is None:
            preferences = {
                "dining_budget": "moderate",
                "preferred_cuisines": ["American", "Italian"],
                "accessibility_needs": False,
                "hiking_interest": True
            }
            
        input_query = f"""
        Plan a trip to Yellowstone National Park for {trip_duration_days} days.
        I'll be starting from {starting_location} and can travel anytime between {travel_window_start.strftime('%Y-%m-%d')} 
        and {travel_window_end.strftime('%Y-%m-%d')}.
        
        Dining preferences: Budget level is {preferences['dining_budget']}, 
        cuisine preferences are {', '.join(preferences['preferred_cuisines'])}.
        
        Accessibility needs: {'Yes' if preferences.get('accessibility_needs') else 'No'}
        Interested in hiking: {'Yes' if preferences.get('hiking_interest') else 'No'}
        
        Coordinate the specialized agents to create a comprehensive trip plan including:
        1. Recommended travel dates based on optimal weather, crowds, and other factors
        2. Weather forecasts for the recommended dates
        3. A detailed route plan from my starting location through key Yellowstone attractions
        4. Restaurant recommendations along the route with reservation options
        """
        
        response = await self.agent.ainvoke({"input": input_query})
        
        # Process and structure the response
        return self._format_response(response, starting_location, trip_duration_days)
    
    def _format_response(self, agent_response, starting_location, trip_duration_days):
        """Format the orchestrator agent response into a structured trip plan"""
        # In production, this would parse and structure the agent output
        # For now, we'll return the raw output with some basic structure
        
        # We would extract these from the orchestrator's coordinated response
        recommended_dates = {}
        weather_forecast = []
        route_plan = {}
        restaurant_recommendations = []
        
        # Try to extract structured data if available in the output
        try:
            # This is simplified - in production, we would have a more robust parser
            output = agent_response["output"]
            
            # Look for JSON or structured data in the response
            # This is just a placeholder for actual structured parsing logic
            if "recommended_dates" in output:
                recommended_dates = self._extract_json_section(output, "recommended_dates")
            
            if "weather_forecast" in output:
                weather_forecast = self._extract_json_section(output, "weather_forecast")
                
            if "route_plan" in output:
                route_plan = self._extract_json_section(output, "route_plan")
                
            if "restaurant_recommendations" in output:
                restaurant_recommendations = self._extract_json_section(output, "restaurant_recommendations")
        
        except Exception as e:
            print(f"Error parsing structured data from response: {str(e)}")
            
        return {
            "starting_location": starting_location,
            "duration_days": trip_duration_days,
            "recommended_dates": recommended_dates or {"reasoning": "Unable to extract structured date recommendations."},
            "weather_forecast": weather_forecast or [],
            "route_plan": route_plan or {},
            "restaurant_recommendations": restaurant_recommendations or [],
            "raw_plan": agent_response["output"]
        }
    
    def _extract_json_section(self, text, section_name):
        """Attempt to extract a JSON section from the text output"""
        try:
            # Very simplified extraction - would be more robust in production
            if f'"{section_name}"' in text or f"'{section_name}'" in text:
                # Find JSON-like content
                start_idx = text.find('{')
                if start_idx != -1:
                    # Find matching closing brace
                    open_count = 1
                    for i in range(start_idx + 1, len(text)):
                        if text[i] == '{':
                            open_count += 1
                        elif text[i] == '}':
                            open_count -= 1
                            if open_count == 0:
                                json_str = text[start_idx:i+1]
                                return json.loads(json_str)
            
            # If not found or not valid JSON, return empty dict/list
            return {} if section_name in ["recommended_dates", "route_plan"] else []
            
        except Exception:
            # Fallback for any parsing errors
            return {} if section_name in ["recommended_dates", "route_plan"] else []
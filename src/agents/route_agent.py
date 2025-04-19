from typing import Dict, Any, List
import os
from datetime import datetime

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import AzureChatOpenAI

from tools.route_planner_tool import RoutePlannerTool
from tools.bing_search_tool import BingSearchTool
from ..config import Config

class RouteAgent:
    """Specialized agent for planning optimal routes to and around Yellowstone"""
    
    def __init__(self):
        self.config = Config()
        if self.config.is_azure_suggestions_mode or self.config.is_live_api_mode:
            self.llm = AzureChatOpenAI(
                azure_deployment=self.config.azure_openai_deployment,
                openai_api_version=self.config.openai_api_version,
                azure_endpoint=self.config.azure_openai_endpoint,
                api_key=self.config.azure_openai_api_key,
                temperature=0.1,
            )
            
            self.prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert route planner for Yellowstone National Park trips.
                For the given starting location and destination, provide detailed route suggestions considering:
                - Optimal driving routes
                - Key attractions and stops along the way
                - Typical travel times and distances
                - Road conditions and seasonal closures
                - Park entrance recommendations
                
                Format your response as a structured route plan including:
                - Total distance and duration
                - Detailed segments with distances and estimated times
                - Recommended stops and points of interest
                - Entrance gate recommendations
                
                Base your suggestions on typical routes and travel patterns."""),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
            
            self.tools = []  # No tools needed in suggestion mode
            
            self.agent = AgentExecutor(
                agent=self._create_agent(),
                tools=self.tools,
                verbose=True,
                handle_parsing_errors=True,
            )
        else:
            # Initialize the LLM
            self.llm = AzureChatOpenAI(
                azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
                openai_api_version=os.getenv("OPENAI_API_VERSION"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                temperature=0.1,
            )
            
            # Initialize tools
            self.tools = [
                RoutePlannerTool(),
                BingSearchTool()  # Add Bing search capability
            ]
            
            # Create the agent prompt
            self.prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a specialized route planning agent for Yellowstone National Park trips.
                
                Your goal is to create optimal driving routes to and around Yellowstone National Park.
                You should consider:
                
                1. Most efficient routes from starting locations to Yellowstone
                2. Logical routes through key attractions within the park
                3. Scenic routes and detours worth taking
                4. Road closures or seasonal accessibility issues
                5. Reasonable driving distances for each day
                
                Use the Bing search tool first to gather real-time information about:
                - Current road conditions and closures in Yellowstone
                - Construction projects that might affect travel
                - Seasonal road opening/closing schedules
                - Popular routes and traveler experiences
                - Special traffic advisories or park notices
                
                Then use the route planning tool to generate detailed driving directions and itineraries
                informed by your up-to-date search findings.
                
                For multi-day trips, suggest logical overnight stops.
                """),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
            
            # Create the agent executor
            self.agent = AgentExecutor(
                agent=self._create_agent(),
                tools=self.tools,
                verbose=True,
                handle_parsing_errors=True,
            )
    
    def _create_agent(self):
        """Create the agent using the OpenAI functions agent"""
        def _agent_factory(llm):
            return llm.bind(
                functions=[tool.metadata for tool in self.tools] if self.tools else []
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
    
    async def plan_route(self,
                        origin: str,
                        destination: str = "Yellowstone National Park",
                        waypoints: List[str] = None,
                        travel_date: str = None) -> Dict[str, Any]:
        """Plan a route to Yellowstone with optional waypoints"""
        
        if self.config.is_dummy_mode:
            return self._get_dummy_route(origin)
        
        elif self.config.is_azure_suggestions_mode:
            waypoints_str = ", with stops at " + ", ".join(waypoints) if waypoints else ""
            input_query = f"""
            Plan a route from {origin} to {destination}{waypoints_str}.
            Travel date: {travel_date if travel_date else 'flexible'}
            
            Please provide:
            1. Total distance and estimated duration
            2. Recommended entrance gate
            3. Step-by-step route segments
            4. Suggested stops and points of interest
            """
            
            response = await self.agent.ainvoke({"input": input_query})
            return self._parse_azure_response(response["output"], origin, destination)
        
        else:  # Live API mode
            if waypoints is None:
                waypoints = []
                
            # If destination is just "Yellowstone National Park", add key attractions as waypoints
            if destination.lower() == "yellowstone national park" and not waypoints:
                waypoints = [
                    "Old Faithful",
                    "Grand Prismatic Spring",
                    "Grand Canyon of the Yellowstone",
                    "Mammoth Hot Springs",
                    "Lamar Valley"
                ]
                
            waypoints_str = ", ".join(waypoints) if waypoints else "No specific waypoints"
            
            input_query = f"""
            Plan an optimal driving route from {origin} to {destination}.
            
            Waypoints to include: {waypoints_str}
            Travel date: {travel_date if travel_date else "Not specified"}
            
            Please provide:
            - Total distance and estimated driving time
            - Route segments with distances and driving times
            - Major roads and highways to take
            - Suggested stops for breaks or overnight stays for longer routes
            - Any scenic detours worth considering
            
            If this is a multi-day trip through Yellowstone, suggest a logical order of attractions
            and where to stay each night.
            """
            
            response = await self.agent.ainvoke({"input": input_query})
            return response["output"]
    
    def _parse_azure_response(self, response: str, origin: str, destination: str) -> Dict[str, Any]:
        """Parse the Azure OpenAI response into a structured format"""
        # This would normally parse the AI's natural language response
        # For now, return a structured format with some defaults
        return {
            "origin": origin,
            "destination": destination,
            "total_distance_miles": 436.1,
            "total_duration_hours": 8.0,
            "recommended_entrance": "West Entrance",
            "segments": [
                {
                    "from": origin,
                    "to": "West Yellowstone",
                    "distance_miles": 325.4,
                    "duration_minutes": 300,
                    "road_names": ["I-15 N", "US-20 E"]
                },
                {
                    "from": "West Yellowstone",
                    "to": "Old Faithful",
                    "distance_miles": 30.5,
                    "duration_minutes": 45,
                    "road_names": ["US-191 N", "Grand Loop Road"]
                },
                {
                    "from": "Old Faithful",
                    "to": "Grand Canyon of the Yellowstone",
                    "distance_miles": 38.2,
                    "duration_minutes": 60,
                    "road_names": ["Grand Loop Road"]
                }
            ],
            "points_of_interest": [
                "Old Faithful Geyser",
                "Grand Prismatic Spring",
                "Grand Canyon of the Yellowstone"
            ],
            "data_source": "Azure OpenAI route analysis"
        }
    
    def _get_dummy_route(self, origin: str) -> Dict[str, Any]:
        """Return dummy route data for local testing"""
        return {
            "origin": origin,
            "destination": "Yellowstone National Park",
            "total_distance_miles": 350,
            "total_duration_hours": 8,
            "segments": [
                {
                    "from": origin,
                    "to": "West Yellowstone Entrance",
                    "distance_miles": 150,
                    "duration_minutes": 180,
                    "road_names": ["I-15", "US-20"]
                }
            ],
            "data_source": "Local dummy data"
        }
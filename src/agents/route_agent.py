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

class RouteAgent:
    """Specialized agent for planning optimal routes to and around Yellowstone"""
    
    def __init__(self):
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
    
    async def plan_route(self,
                        origin: str,
                        destination: str,
                        waypoints: List[str] = None,
                        travel_date: str = None) -> Dict[str, Any]:
        """Plan an optimal route from origin to destination with optional waypoints"""
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
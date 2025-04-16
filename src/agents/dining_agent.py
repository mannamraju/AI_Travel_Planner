from typing import Dict, Any, List
import os
from datetime import datetime, timedelta

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import AzureChatOpenAI

from tools.restaurant_tool import RestaurantTool
from tools.reservation_tool import ReservationTool
from tools.bing_search_tool import BingSearchTool

class DiningAgent:
    """Specialized agent for restaurant recommendations and reservations"""
    
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
            RestaurantTool(),
            ReservationTool(),
            BingSearchTool()  # Add Bing search capability
        ]
        
        # Create the agent prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a specialized dining agent for Yellowstone National Park trips.
            
            Your goal is to provide excellent restaurant recommendations along travel routes
            and assist with making reservations. You should consider:
            
            1. Restaurant options in different locations along the route
            2. Diverse dining options matching user preferences
            3. Price points and cuisine types
            4. Reservation availability for popular establishments
            
            Use the Bing search tool first to gather up-to-date information about:
            - New restaurants or dining options that have recently opened
            - Seasonal restaurant schedules and hours in the Yellowstone area
            - Recent reviews and ratings of restaurants
            - Special dining events or unique culinary experiences
            - Food trucks or pop-up dining options during the travel dates
            
            Then use the restaurant finder tool to search for options and the reservation tool
            to check availability and make bookings. Focus on providing practical and
            high-quality dining options that enhance the travel experience.
            
            Incorporate the real-time information from your searches into your recommendations.
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
    
    async def get_recommendations(self,
                                 locations: List[str],
                                 cuisine_preferences: List[str] = None,
                                 price_level: str = "moderate",
                                 travel_dates: List[str] = None) -> Dict[str, Any]:
        """Get restaurant recommendations for specified locations and preferences"""
        if cuisine_preferences is None:
            cuisine_preferences = ["American", "Italian"]
            
        if travel_dates is None:
            # If no dates provided, use a near future date
            today = datetime.now()
            future_date = today + timedelta(days=30)
            travel_dates = [future_date.strftime("%Y-%m-%d")]
            
        cuisine_str = ", ".join(cuisine_preferences)
        locations_str = ", ".join(locations)
        dates_str = ", ".join(travel_dates)
        
        input_query = f"""
        Find restaurant recommendations for the following locations along a Yellowstone trip route: {locations_str}
        
        Preferences:
        - Cuisine types: {cuisine_str}
        - Price level: {price_level}
        - Travel dates: {dates_str}
        
        For each location, please recommend 2-3 restaurants that:
        - Match the cuisine preferences when possible
        - Are within the specified price level
        - Have good ratings and reviews
        - Are conveniently located for travelers
        
        For highly-rated restaurants, check reservation availability for the travel dates provided.
        Provide a comprehensive list of dining options organized by location.
        """
        
        response = await self.agent.ainvoke({"input": input_query})
        return response["output"]
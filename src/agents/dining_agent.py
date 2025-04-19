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
from ..config import Config

class DiningAgent:
    """Specialized agent for restaurant recommendations and reservations"""
    
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
                ("system", """You are an expert dining guide for Yellowstone National Park and surrounding areas.
                For given locations and preferences, recommend restaurants considering:
                - Cuisine types and dietary preferences
                - Price points and budget levels
                - Location convenience for travelers
                - Popular dishes and specialties
                - Typical wait times and reservation needs
                
                Format your response as structured recommendations including:
                - Restaurant name and location
                - Cuisine type and price level
                - Key dishes and specialties
                - Reservation guidance
                - Tips for dining experience
                
                Base your suggestions on typical dining patterns and local knowledge."""),
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
            # Initialize the LLM for other modes
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
                BingSearchTool()
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
                
                Incorporate the real-time information from your searches into your recommendations."""),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
            
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
    
    async def get_recommendations(self,
                                 locations: List[str],
                                 cuisine_preferences: List[str] = None,
                                 price_level: str = "moderate",
                                 travel_dates: List[str] = None) -> Dict[str, Any]:
        """Get restaurant recommendations for specified locations and preferences"""
        if self.config.is_dummy_mode:
            return self._get_dummy_recommendations(locations)
            
        elif self.config.is_azure_suggestions_mode:
            if cuisine_preferences is None:
                cuisine_preferences = ["American", "Italian"]
                
            if travel_dates is None:
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
            
            For highly-rated restaurants, include tips about reservation needs.
            Provide a comprehensive list of dining options organized by location.
            """
            
            response = await self.agent.ainvoke({"input": input_query})
            return self._parse_azure_response(response["output"], locations)
            
        else:  # Live API mode
            raise NotImplementedError("Live API mode not implemented yet")
    
    def _parse_azure_response(self, response: str, locations: List[str]) -> Dict[str, Any]:
        """Parse the Azure OpenAI response into a structured format"""
        # This would normally parse the AI's natural language response
        # For now, return a structured format with some defaults
        recommendations = []
        
        # Generate recommendations for each location
        for location in locations:
            recommendations.extend([
                {
                    "name": "Old Faithful Inn Dining Room",
                    "cuisine": "American",
                    "price_level": "moderate",
                    "location": location,
                    "rating": 4.5,
                    "description": "Historic dining room with classic American cuisine",
                    "signature_dishes": ["Bison Burger", "Rainbow Trout"],
                    "accepts_reservations": True,
                    "available_times": ["5:00 PM", "6:30 PM", "8:00 PM"]
                },
                {
                    "name": "Lake Lodge Cafeteria",
                    "cuisine": "American",
                    "price_level": "budget",
                    "location": location,
                    "rating": 4.0,
                    "description": "Casual dining with great lake views",
                    "signature_dishes": ["Montana Meatloaf", "Huckleberry Pie"],
                    "accepts_reservations": False
                }
            ])
        
        return {
            "restaurants": recommendations,
            "data_source": "Azure OpenAI dining analysis"
        }
    
    def _get_dummy_recommendations(self, locations: List[str]) -> Dict[str, Any]:
        """Return dummy restaurant recommendations for local testing"""
        recommendations = []
        
        for location in locations:
            recommendations.append({
                "name": "Test Restaurant",
                "cuisine": "American",
                "price_level": "moderate",
                "location": location,
                "rating": 4.0
            })
        
        return {
            "restaurants": recommendations,
            "data_source": "Local dummy data"
        }
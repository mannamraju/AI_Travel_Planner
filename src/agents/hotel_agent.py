from typing import Dict, Any, List
import os
from datetime import datetime, timedelta

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import AzureChatOpenAI

from tools.hotel_tool import HotelTool
from tools.hotel_reservation_tool import HotelReservationTool
from tools.bing_search_tool import BingSearchTool
from ..config import Config

class HotelAgent:
    """Specialized agent for hotel search and reservations"""
    
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
                ("system", """You are an expert hotel advisor for Yellowstone National Park and surrounding areas.
                For given locations and preferences, recommend accommodations considering:
                - Location convenience and park access
                - Room types and amenities
                - Price points and value
                - Peak season availability
                - Special features (views, historic significance, etc.)
                
                Format your response as structured recommendations including:
                - Hotel name and location
                - Room types and rates
                - Key amenities and features
                - Booking guidance and tips
                - Special considerations
                
                Base your suggestions on typical patterns and local knowledge."""),
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
                HotelTool(),
                HotelReservationTool(),
                BingSearchTool()
            ]
            
            # Create the agent prompt
            self.prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a specialized hotel agent for Yellowstone National Park trips.
                
                Your goal is to provide excellent hotel recommendations based on user preferences and
                assist with making reservations. You should consider:
                
                1. Location preferences (proximity to park entrances or attractions)
                2. Budget constraints and price ranges
                3. Accommodation types (hotel, cabin, lodge, etc.)
                4. Amenities requested (WiFi, breakfast, pool, etc.)
                5. Availability during the specified dates
                
                Use the Bing search tool first to gather up-to-date information about:
                - Seasonal hotel availability around Yellowstone
                - Current rates and special offers
                - Recent reviews about accommodations
                - Any construction or renovation work at hotels
                - Special events that might affect accommodation availability
                
                Then use the hotel search tool to find suitable options and the hotel reservation tool
                to check availability and make bookings.
                
                For each hotel recommendation, provide:
                - Key amenities and features
                - Proximity to park entrances or attractions
                - Price per night and total cost for the stay
                - Brief description of what makes this hotel a good match
                
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
                                check_in_date: str,
                                check_out_date: str,
                                guests: int = 2,
                                max_price: float = None,
                                amenities: List[str] = None) -> Dict[str, Any]:
        """Get hotel recommendations for specified locations and dates"""
        if self.config.is_dummy_mode:
            return self._get_dummy_recommendations(locations)
            
        elif self.config.is_azure_suggestions_mode:
            if amenities is None:
                amenities = ["WiFi", "Parking"]
                
            locations_str = ", ".join(locations)
            amenities_str = ", ".join(amenities)
            price_str = f"under ${max_price} per night" if max_price else "any price range"
            
            input_query = f"""
            Find hotel recommendations for the following locations near Yellowstone: {locations_str}
            
            Stay details:
            - Check-in: {check_in_date}
            - Check-out: {check_out_date}
            - Number of guests: {guests}
            - Price range: {price_str}
            - Desired amenities: {amenities_str}
            
            For each location, please recommend 2-3 hotels that:
            - Are conveniently located for park access
            - Offer good value for the price point
            - Include the requested amenities when possible
            - Have positive guest reviews
            
            Include information about:
            - Room types and rates
            - Key amenities and features
            - Location benefits
            - Booking tips or special considerations
            """
            
            response = await self.agent.ainvoke({"input": input_query})
            return self._parse_azure_response(response["output"], locations, check_in_date, check_out_date)
            
        else:  # Live API mode
            raise NotImplementedError("Live API mode not implemented yet")
    
    def _parse_azure_response(self, response: str, locations: List[str], 
                            check_in_date: str, check_out_date: str) -> Dict[str, Any]:
        """Parse the Azure OpenAI response into a structured format"""
        # This would normally parse the AI's natural language response
        # For now, return a structured format with some defaults
        recommendations = []
        
        # Generate recommendations for each location
        for location in locations:
            recommendations.extend([
                {
                    "name": "Old Faithful Inn",
                    "location": location,
                    "type": "Historic Lodge",
                    "price_per_night": 259,
                    "rating": 4.7,
                    "amenities": ["Restaurant", "Historic Building", "Geyser Views"],
                    "description": "Iconic lodge with prime location near Old Faithful",
                    "room_types": ["Standard Room", "Suite"],
                    "availability": True,
                    "booking_tips": "Book 6-12 months in advance for summer stays"
                },
                {
                    "name": "Lake Lodge Cabins",
                    "location": location,
                    "type": "Cabin",
                    "price_per_night": 189,
                    "rating": 4.3,
                    "amenities": ["Kitchenette", "Lake Views", "Parking"],
                    "description": "Cozy cabins with beautiful lake views",
                    "room_types": ["Western Cabin", "Frontier Cabin"],
                    "availability": True,
                    "booking_tips": "Western Cabins offer more amenities"
                }
            ])
        
        return {
            "hotels": recommendations,
            "check_in": check_in_date,
            "check_out": check_out_date,
            "data_source": "Azure OpenAI accommodation analysis"
        }
    
    def _get_dummy_recommendations(self, locations: List[str]) -> Dict[str, Any]:
        """Return dummy hotel recommendations for local testing"""
        recommendations = []
        
        for location in locations:
            recommendations.append({
                "name": "Test Hotel",
                "location": location,
                "type": "Hotel",
                "price_per_night": 200,
                "rating": 4.0,
                "amenities": ["WiFi", "Parking"]
            })
        
        return {
            "hotels": recommendations,
            "data_source": "Local dummy data"
        }
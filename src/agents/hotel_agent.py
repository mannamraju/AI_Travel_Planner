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

class HotelAgent:
    """Specialized agent for hotel search and reservations"""
    
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
        """Create an OpenAI functions agent"""
        prompt = self.prompt
        llm_with_tools = self.llm.bind_functions(self.tools)
        
        def agent(input, agent_scratchpad):
            messages = prompt.format_messages(
                input=input,
                agent_scratchpad=agent_scratchpad,
            )
            return llm_with_tools.invoke(messages)
        
        return {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_function_messages(x["intermediate_steps"]),
            "llm": llm_with_tools,
        }
    
    def run(self, input_data):
        """Run the agent with the provided input"""
        return self.agent.invoke({"input": input_data})
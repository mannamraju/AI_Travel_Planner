from typing import Dict, Any, List
import os
from datetime import datetime, timedelta

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import AzureChatOpenAI

from tools.weather_tool import WeatherTool
from tools.bing_search_tool import BingSearchTool

class WeatherAgent:
    """Specialized agent for weather forecasting for Yellowstone trips"""
    
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
            WeatherTool(),
            BingSearchTool()  # Add Bing search capability
        ]
        
        # Create the agent prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a specialized weather forecasting agent for Yellowstone National Park trips.
            
            Your goal is to provide accurate and helpful weather forecasts for specific locations
            and dates in and around Yellowstone. You should consider:
            
            1. Temperature ranges (highs and lows)
            2. Precipitation chances and types
            3. Weather conditions that might impact outdoor activities
            4. Weather patterns that could affect road conditions
            
            Use the Bing search tool to first gather:
            - Recent weather patterns or anomalies in the Yellowstone region
            - Seasonal weather trends for the specific dates requested
            - Current forecasts from official sources like the National Weather Service
            - Weather-related alerts or warnings affecting the area
            
            Then use the weather tool to get the most accurate forecasts available
            and combine with your search findings to provide comprehensive guidance.
            
            Provide weather data that travelers can use to pack appropriately and plan activities.
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
    
    async def get_forecast(self,
                          location: str,
                          start_date: str,
                          end_date: str) -> Dict[str, Any]:
        """Get weather forecasts for a specific location and date range"""
        
        input_query = f"""
        Provide a detailed weather forecast for {location} from {start_date} to {end_date}.
        
        Please include:
        - Daily high and low temperatures
        - Precipitation chances
        - Weather conditions
        - Any weather alerts or notable patterns
        
        Format the information in a way that's easy to understand for trip planning purposes.
        Provide any relevant recommendations based on the weather forecast (e.g., "Bring rain gear for Wednesday").
        """
        
        response = await self.agent.ainvoke({"input": input_query})
        return response["output"]
from typing import Dict, Any, List
import os
from datetime import datetime, timedelta

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import AzureChatOpenAI

from ..config import Config
from tools.weather_tool import WeatherTool
from tools.bing_search_tool import BingSearchTool

class WeatherAgent:
    """Specialized agent for weather forecasting for Yellowstone trips"""
    
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
                ("system", """You are an expert weather forecaster for Yellowstone National Park.
                For the given dates and location, provide detailed weather forecasts considering:
                - Historical weather patterns for those dates
                - Typical temperatures and conditions for the season
                - Impact on park activities and accessibility
                
                Format your response as a structured forecast including:
                - Daily high and low temperatures (in Fahrenheit)
                - Precipitation chances
                - General conditions
                - Any relevant weather advisories
                
                Base your suggestions on typical weather patterns and historical data."""),
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
    
    async def get_forecast(self,
                          location: str,
                          start_date: str,
                          end_date: str) -> Dict[str, Any]:
        """Get weather forecasts for a specific location and date range"""
        
        if self.config.is_dummy_mode:
            return self._get_dummy_forecast(start_date, end_date)
        
        elif self.config.is_azure_suggestions_mode:
            input_query = f"""
            Provide a weather forecast for {location} from {start_date} to {end_date}.
            Consider typical weather patterns for Yellowstone during this time period.
            """
            response = await self.agent.ainvoke({"input": input_query})
            return self._parse_azure_response(response["output"], start_date, end_date)
        
        else:  # Live API mode
            # Will implement real API calls here in Mode 3
            raise NotImplementedError("Live API mode not implemented yet")
    
    def _parse_azure_response(self, response: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Parse the Azure OpenAI response into a structured format"""
        # For now, return a structured format based on the AI's natural language response
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end - start).days + 1
        
        # Extract temperature and condition information from the response
        # This is a simple implementation - could be made more sophisticated
        forecasts = []
        current_date = start
        for _ in range(days):
            forecasts.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "condition": "Partly Cloudy",  # Extract from response
                "high_temp_f": 75,  # Extract from response
                "low_temp_f": 45,  # Extract from response
                "precipitation_chance": 20,  # Extract from response
                "description": response[:100]  # Use first part of response as description
            })
            current_date += timedelta(days=1)
        
        return {
            "location": "Yellowstone National Park",
            "forecasts": forecasts,
            "advisory": "Based on typical weather patterns for this time of year.",
            "data_source": "Azure OpenAI weather pattern analysis"
        }
    
    def _get_dummy_forecast(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Return dummy forecast data for local testing"""
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end - start).days + 1
        
        forecasts = []
        current_date = start
        for _ in range(days):
            forecasts.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "condition": "Sunny",
                "high_temp_f": 75,
                "low_temp_f": 45,
                "precipitation_chance": 10
            })
            current_date += timedelta(days=1)
        
        return {
            "location": "Yellowstone National Park",
            "forecasts": forecasts,
            "data_source": "Local dummy data"
        }
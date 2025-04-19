from typing import Optional, Dict, Any
import os
from datetime import datetime, timedelta
import random

from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import AzureChatOpenAI

from tools.calendar_tool import CalendarOptimizerTool
from tools.bing_search_tool import BingSearchTool
from ..config import Config

class CalendarAgent:
    """Specialized agent for finding optimal travel dates for Yellowstone trips"""
    
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
                ("system", """You are an expert travel date optimizer for Yellowstone National Park.
                For the given travel window and duration, suggest optimal dates considering:
                - Seasonal weather patterns and park accessibility
                - Historical crowd levels and peak/off-peak periods
                - Wildlife activity and migration patterns
                - Special events and park programs
                
                Format your response as structured date recommendations including:
                - Multiple date range options
                - Detailed reasoning for each suggestion
                - Pros and cons of each time period
                - Tips for making the most of the chosen dates
                
                Base your suggestions on typical patterns and historical data."""),
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
                CalendarOptimizerTool(),
                BingSearchTool()
            ]
            
            # Create the agent prompt
            self.prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a specialized agent focused on finding optimal travel dates 
                for Yellowstone National Park trips.
                
                Your goal is to identify the best dates for a Yellowstone trip based on:
                1. Weather patterns
                2. Crowd levels
                3. Wildlife viewing opportunities
                4. Seasonal attractions
                
                Use the Bing search tool to first gather up-to-date information about:
                - Current park conditions and seasonal road openings
                - Special events or festivals happening in Yellowstone
                - Recent news about wildlife activity patterns
                - Latest crowd forecasts and visitation trends
                
                Then use the calendar optimization tool to analyze these factors and recommend 
                the ideal travel dates within the user's available window.
                
                Provide thoughtful explanations for your recommendations based on the real-time 
                information you've gathered from web searches."""),
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

    async def get_optimal_dates(self, 
                               travel_window_start: str,
                               travel_window_end: str,
                               trip_duration_days: int,
                               preferred_day_of_week_start: Optional[str] = None) -> Dict[str, Any]:
        """Find optimal travel dates within the specified window"""
        if self.config.is_dummy_mode:
            return self._get_dummy_dates(travel_window_start, travel_window_end, trip_duration_days)
            
        elif self.config.is_azure_suggestions_mode:
            input_query = f"""
            Find the optimal travel dates for a {trip_duration_days}-day trip to Yellowstone National Park.
            
            Available travel window: {travel_window_start} to {travel_window_end}
            {f"Preferred start day of week: {preferred_day_of_week_start}" if preferred_day_of_week_start else "No preferred start day of week."}
            
            Please recommend the best dates within this window, considering:
            - Weather conditions
            - Crowd levels
            - Wildlife viewing opportunities
            - Seasonal park attractions and accessibility
            
            Provide 2-3 date range options ranked by overall desirability, with clear reasoning for each recommendation.
            """
            
            response = await self.agent.ainvoke({"input": input_query})
            return self._parse_azure_response(response["output"], travel_window_start, travel_window_end, trip_duration_days)
            
        else:  # Live API mode
            input_query = f"""
            Find optimal travel dates for a {trip_duration_days}-day trip to Yellowstone National Park.
            
            Available travel window: {travel_window_start} to {travel_window_end}
            {f"Preferred start day of week: {preferred_day_of_week_start}" if preferred_day_of_week_start else "No preferred start day of week."}
            
            Please recommend the best dates within this window, considering:
            - Weather conditions and seasonal patterns
            - Expected crowd levels and peak periods
            - Wildlife viewing opportunities
            - Park attraction availability and accessibility
            
            First, search for current information about park conditions, events, and seasonal factors.
            Then, use the calendar optimization tool to find the best dates based on this information.
            
            Provide multiple date range options with detailed reasoning for each recommendation.
            """
            
            response = await self.agent.ainvoke({"input": input_query})
            return response["output"]
    
    def _parse_azure_response(self, response: str, 
                            travel_window_start: str,
                            travel_window_end: str,
                            trip_duration_days: int) -> Dict[str, Any]:
        """Parse the Azure OpenAI response into a structured format"""
        # This would normally parse the AI's natural language response
        # For now, return a structured format with some defaults
        start = datetime.strptime(travel_window_start, "%Y-%m-%d")
        end = datetime.strptime(travel_window_end, "%Y-%m-%d")
        days_range = (end - start).days
        
        # Generate 3 recommended date ranges
        recommendations = []
        current_date = start
        for i in range(3):
            if current_date + timedelta(days=trip_duration_days) <= end:
                range_end = current_date + timedelta(days=trip_duration_days-1)
                recommendations.append({
                    "start_date": current_date.strftime("%Y-%m-%d"),
                    "end_date": range_end.strftime("%Y-%m-%d"),
                    "total_score": 0.9 - (i * 0.05),  # Decreasing scores
                    "weather_score": 0.88 - (i * 0.03),
                    "crowd_score": 0.85 - (i * 0.04),
                    "wildlife_score": 0.92 - (i * 0.03)
                })
                current_date += timedelta(days=max(10, days_range // 4))  # Space out recommendations
        
        return {
            "recommended_date_ranges": recommendations,
            "reasoning": response[:200] if len(response) > 200 else response,  # Include part of the detailed reasoning
            "data_source": "Azure OpenAI analysis of historical patterns"
        }
    
    def _get_dummy_dates(self, travel_window_start: str, 
                        travel_window_end: str,
                        trip_duration_days: int) -> Dict[str, Any]:
        """Return dummy date recommendations for local testing"""
        start = datetime.strptime(travel_window_start, "%Y-%m-%d")
        recommended_start = start + timedelta(days=random.randint(7, 14))
        recommended_end = recommended_start + timedelta(days=trip_duration_days-1)
        
        return {
            "recommended_date_ranges": [{
                "start_date": recommended_start.strftime("%Y-%m-%d"),
                "end_date": recommended_end.strftime("%Y-%m-%d"),
                "total_score": 0.85,
                "weather_score": 0.8,
                "crowd_score": 0.9,
                "wildlife_score": 0.85
            }],
            "reasoning": "Dummy recommendation for testing",
            "data_source": "Local dummy data"
        }
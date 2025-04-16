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

class CalendarAgent:
    """Specialized agent for finding optimal travel dates for Yellowstone trips"""
    
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
            CalendarOptimizerTool(),
            BingSearchTool()  # Add Bing search capability
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
            information you've gathered from web searches.
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
    
    async def get_optimal_dates(self, 
                               travel_window_start: str,
                               travel_window_end: str,
                               trip_duration_days: int,
                               preferred_day_of_week_start: Optional[str] = None) -> Dict[str, Any]:
        """Find optimal travel dates within the specified window"""
        
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
        return response["output"]
from pydantic import BaseModel, Field
import os
import aiohttp
import json
from typing import List, Dict, Any
import asyncio

from .base_tool import CustomBaseTool

class BingSearchRequest(BaseModel):
    query: str = Field(..., description="Search query to send to Bing")
    count: int = Field(default=5, description="Number of results to return (max 50)")

class BingSearchTool(CustomBaseTool):
    name = "bing_search"
    description = "Search the web for up-to-date information via Bing"
    args_schema = BingSearchRequest
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("BING_SEARCH_API_KEY")
        self.endpoint = "https://api.bing.microsoft.com/v7.0/search"
        
        # Provide a mock API key for development if not set in environment
        if not self.api_key:
            print("Warning: BING_SEARCH_API_KEY not set in environment variables. Using mock data.")
    
    def _run(self, query: str, count: int = 5) -> List[Dict[str, Any]]:
        """Execute a Bing search and return results"""
        return asyncio.run(self._arun(query, count))
    
    async def _arun(self, query: str, count: int = 5) -> List[Dict[str, Any]]:
        """Async implementation of the Bing search"""
        if not self.api_key:
            return self._get_mock_results(query)
            
        try:
            headers = {
                'Ocp-Apim-Subscription-Key': self.api_key
            }
            
            # Using context managers for proper cleanup
            async with aiohttp.ClientSession() as session:
                # Disable SSL verification
                conn = aiohttp.TCPConnector(ssl=False)
                async with session.get(
                    self.endpoint,
                    params={'q': query, 'count': str(count)},
                    headers=headers,
                    connector=conn
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Warning: Bing API returned status code {response.status}")
                        return self._get_mock_results(query)
                
        except Exception as e:
            print(f"Warning: Error calling Bing API: {e}")
            return self._get_mock_results(query)
    
    def _get_mock_results(self, query: str) -> List[Dict[str, Any]]:
        """Return mock results for testing"""
        return {
            "webPages": {
                "value": [
                    {
                        "name": "Yellowstone National Park",
                        "url": "https://www.nps.gov/yell/",
                        "snippet": "Mock search result about Yellowstone"
                    }
                ]
            }
        }
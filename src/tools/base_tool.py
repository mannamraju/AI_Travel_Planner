from typing import Any, Dict, Optional
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field

class CustomBaseTool(ABC):
    """Base tool class that doesn't depend on requests/certifi"""
    name: str
    description: str
    args_schema: Optional[type[BaseModel]] = None
    
    def __init__(self):
        if not hasattr(self, "name"):
            raise ValueError("Tool must have a name")
        if not hasattr(self, "description"):
            raise ValueError("Tool must have a description")
    
    @abstractmethod
    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """Use the tool."""
        pass
    
    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        """Use the tool asynchronously."""
        raise NotImplementedError("Tool does not support async")
    
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Call the tool."""
        return self._run(*args, **kwargs)
from enum import Enum
import os
from typing import Optional

class AppMode(Enum):
    LOCAL_DUMMY = 1  # Local testing with dummy data
    AZURE_SUGGESTIONS = 2  # Use Azure OpenAI for suggestions
    LIVE_API = 3  # Use real third-party APIs

class Config:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.app_mode = AppMode(int(os.getenv('APP_MODE', '1')))
        self.azure_openai_deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT')
        self.azure_openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.azure_openai_api_key = os.getenv('AZURE_OPENAI_API_KEY')
        self.openai_api_version = os.getenv('OPENAI_API_VERSION', '2024-02-15-preview')

    @property
    def is_dummy_mode(self) -> bool:
        return self.app_mode == AppMode.LOCAL_DUMMY
    
    @property
    def is_azure_suggestions_mode(self) -> bool:
        return self.app_mode == AppMode.AZURE_SUGGESTIONS
    
    @property
    def is_live_api_mode(self) -> bool:
        return self.app_mode == AppMode.LIVE_API
    
    def validate_azure_config(self) -> Optional[str]:
        """Validate Azure OpenAI configuration when needed"""
        if self.is_azure_suggestions_mode or self.is_live_api_mode:
            missing = []
            if not self.azure_openai_deployment:
                missing.append("AZURE_OPENAI_DEPLOYMENT")
            if not self.azure_openai_endpoint:
                missing.append("AZURE_OPENAI_ENDPOINT")
            if not self.azure_openai_api_key:
                missing.append("AZURE_OPENAI_API_KEY")
            
            if missing:
                return f"Missing required Azure OpenAI configuration: {', '.join(missing)}"
        return None
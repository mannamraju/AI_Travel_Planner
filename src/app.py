import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pydantic import BaseModel

from config import Config
from agents.trip_planner import YellowstoneTripPlanner

app = FastAPI()
config = Config()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TripRequest(BaseModel):
    starting_location: str
    travel_window_start: datetime
    travel_window_end: datetime
    trip_duration_days: int
    preferences: Optional[Dict[str, Any]] = None

@app.get("/")
async def root():
    mode_names = {
        1: "Local Dummy Data",
        2: "Azure OpenAI Suggestions",
        3: "Live API Integration"
    }
    return {
        "message": "Server is running",
        "mode": mode_names.get(config.app_mode.value, "Unknown"),
        "status": "ready"
    }

@app.post("/api/plan-trip")
async def plan_trip(request: TripRequest):
    # Validate Azure configuration if needed
    if config.is_azure_suggestions_mode:
        error = config.validate_azure_config()
        if error:
            raise HTTPException(status_code=500, detail=error)
    
    # Initialize trip planner with current mode
    trip_planner = YellowstoneTripPlanner()
    
    try:
        trip_plan = await trip_planner.plan_trip(
            starting_location=request.starting_location,
            travel_window_start=request.travel_window_start,
            travel_window_end=request.travel_window_end,
            trip_duration_days=request.trip_duration_days,
            preferences=request.preferences
        )
        return trip_plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
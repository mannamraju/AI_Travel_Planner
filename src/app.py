import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from agents.trip_planner import YellowstoneTripPlanner
from services.auth_service import get_current_user
from models.trip_request import TripRequest, TripResponse

# Load environment variables
# First try to load from .keys file for local development
keys_path = Path(__file__).parents[1] / '.keys'
if keys_path.exists():
    print(f"Loading development environment from {keys_path}")
    load_dotenv(dotenv_path=keys_path)
else:
    # Fall back to regular .env file or environment variables
    print("No .keys file found, using environment variables")
    load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Yellowstone Trip Planner")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent
trip_planner = YellowstoneTripPlanner()

# Routes
@app.post("/api/plan-trip", response_model=TripResponse)
async def plan_trip(request: TripRequest, user=Depends(get_current_user)):
    """Generate a trip plan for Yellowstone National Park"""
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

# Mount static files for the frontend
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
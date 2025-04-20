# AI-Powered Trip Planner - Project Guide

## Project Overview

The AI-Powered Trip Planner is an intelligent application that helps users plan comprehensive trips to their desired destinations. It leverages AI agents, modern web technologies, and external APIs to create personalized trip plans with optimal dates, routes, weather forecasts, and dining recommendations.

## Architecture

The application follows a parallel agent architecture with specialized agents coordinated by an orchestrator:

```
                           ┌───────────────────┐
                           │   Trip Planner    │
                           │    (Main Entry)   │
                           └─────────┬─────────┘
                                     │
                           ┌─────────▼─────────┐
                           │    Orchestrator   │
                           │       Agent       │
                           └─────────┬─────────┘
                                     │
                 ┌───────────────────┼───────────────────┐
                 │                   │                   │
         ┌───────▼───────┐   ┌───────▼───────┐   ┌───────▼───────┐
         │   Calendar    │   │    Weather    │   │     Route     │
         │     Agent     │   │     Agent     │   │     Agent     │
         └───────────────┘   └───────┬───────┘   └───────┬───────┘
                                     │                   │
                                     │             ┌─────▼─────┐
                                     │             │  Dining   │
                                     │             │   Agent   │
                                     │             └───────────┘
                                     │
                           ┌─────────▼─────────┐
                           │       APIs        │
                           │ (Weather, Maps,   │
                           │  Restaurants)     │
                           └───────────────────┘
```

## Modules

### Backend Components

#### 1. Agents

The agent system follows a hierarchical structure where specialized agents are coordinated by an orchestrator:

| Module | Purpose | Description |
|--------|---------|-------------|
| `trip_planner.py` | Entry Point | Main interface that clients interact with, delegates to the orchestrator |
| `orchestrator_agent.py` | Coordination | Manages workflow and parallel execution of specialized agents |
| `calendar_agent.py` | Date Optimization | Finds optimal travel dates based on multiple factors |
| `weather_agent.py` | Weather Forecasting | Provides weather data for specific locations and dates |
| `route_agent.py` | Route Planning | Creates optimal driving routes between destinations |
| `dining_agent.py` | Restaurant Finder | Recommends restaurants along routes with reservation capabilities |

#### 2. Tools

Tools are specialized modules that agents use to accomplish specific tasks:

| Module | Purpose | Description |
|--------|---------|-------------|
| `weather_tool.py` | API Integration | Connects to Open Weather API to fetch real-time weather data |
| `route_planner_tool.py` | Routing | Calculates optimal routes, distances, and travel times |
| `restaurant_tool.py` | Restaurant Search | Finds dining options based on location and preferences |
| `reservation_tool.py` | Booking | Checks availability and books restaurant reservations |
| `calendar_tool.py` | Date Analysis | Analyzes optimal travel dates based on multiple factors |

#### 3. Models

Data structures that define the application's inputs and outputs:

| Module | Purpose | Description |
|--------|---------|-------------|
| `trip_request.py` | Data Definition | Defines the structure of trip requests and responses |

#### 4. Services

Support services for application functionality:

| Module | Purpose | Description |
|--------|---------|-------------|
| `auth_service.py` | Authentication | Manages user authentication and authorization |
| `app.py` | API Service | FastAPI application that exposes endpoints and serves the frontend |

### Frontend Components

#### 1. Core Components

| Module | Purpose | Description |
|--------|---------|-------------|
| `App.js` | Main Component | Central React component that manages application state |
| `index.js` | Entry Point | React application entry point |

#### 2. Feature Components

| Module | Purpose | Description |
|--------|---------|-------------|
| `TripForm.js` | User Input | Collects trip parameters and preferences from users |
| `TripResults.js` | Display | Presents comprehensive trip plans with interactive features |

#### 3. Styling

| Module | Purpose | Description |
|--------|---------|-------------|
| `App.css` | Main Styling | Core application styling |
| `TripForm.css` | Form Styling | Styling for the trip planning form |
| `TripResults.css` | Results Styling | Styling for the trip results display |

### Infrastructure

| Module | Purpose | Description |
|--------|---------|-------------|
| `main.bicep` | Azure Deployment | Infrastructure as Code for Azure deployment |

## Workflow

1. **User Input**: Users enter their trip preferences through the TripForm component
2. **Backend Processing**:
   - The orchestrator agent coordinates the planning process
   - Calendar agent determines optimal dates
   - Weather and route agents work in parallel once dates are known
   - Dining agent uses route information to find restaurant recommendations
3. **Response**: A comprehensive trip plan is returned to the frontend
4. **Display**: The TripResults component presents the plan with interactive features

## Key Features

- **Parallel Agent Architecture**: Specialized agents work simultaneously when possible
- **Real-time Weather Integration**: Weather forecasts for travel destinations
- **Intelligent Date Selection**: Optimal dates based on weather, events, and local factors
- **Interactive UI**: User-friendly interface for both inputting preferences and viewing results
- **Reservation Capabilities**: Restaurant and accommodation recommendations with availability information

## Technology Stack

- **Backend**: Python, FastAPI, LangChain, Azure OpenAI
- **Frontend**: React, CSS3
- **APIs**: Open Weather API, Maps APIs, Restaurant APIs
- **Infrastructure**: Azure, Bicep (IaC)

## Development Setup

The application supports three distinct operating modes:

1. **Local Testing Mode (Mode 1)**
   - Returns randomized dummy data for quick testing
   - No external API calls or Azure OpenAI usage
   - Useful for UI development and basic flow testing
   - Set `APP_MODE=1` in .env file

2. **Azure Suggestions Mode (Mode 2)**
   - Uses Azure OpenAI to generate intelligent suggestions
   - Based on historical patterns and expert knowledge
   - No external API calls, but requires Azure OpenAI credentials
   - Set `APP_MODE=2` in .env file

3. **Live API Mode (Mode 3)**
   - Makes real API calls to external services
   - Uses actual weather, route, and restaurant data
   - Requires all API credentials to be configured
   - Set `APP_MODE=3` in .env file

### Environment Configuration

Create a `.env` file in the root directory with the following variables:

```
APP_MODE=2  # Choose mode 1, 2, or 3
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_ENDPOINT=your-endpoint
AZURE_OPENAI_API_KEY=your-api-key
OPENAI_API_VERSION=2024-02-15-preview  # Or your preferred version
```

Alternatively, you can store your Azure OpenAI credentials in a `.keys` file in the root directory. The application will automatically read credentials from this file if present.

### Running Locally

1. Install dependencies:
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

2. Start the backend server:
```bash
# Start with proper handling of node_modules directory
uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload-exclude="**/node_modules/**"
```

3. In a separate terminal, start the frontend:
```bash
cd frontend
npm start
```

The application will be available at:
- Backend API: http://localhost:8000
- Frontend UI: http://localhost:3000

### Key Dependencies

#### Backend
- FastAPI for the API server
- Uvicorn for ASGI server
- LangChain and LangChain OpenAI for AI capabilities
- Aiohttp for async HTTP requests
- Watchfiles for improved development reloading
- Python-dotenv for environment management

#### Frontend
- React for UI components
- React Router for navigation
- Axios for API requests

See the README.md file for additional setup instructions, including API keys and local testing.

## Deployment

The application can be deployed to Azure using the Bicep template in the infrastructure directory.

```bash
az login
az deployment group create --resource-group YourResourceGroup --template-file infrastructure/main.bicep
```
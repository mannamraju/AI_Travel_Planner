# Trip Planner with Agentic AI

An intelligent trip planning application for Yellowstone National Park powered by LangChain and Azure OpenAI.

## Features

- AI-powered trip planning using declarative agents
- Weather forecasting based on historical and real-time data
- Route optimization for travel to and around Yellowstone
- Restaurant recommendations with reservation capabilities
- Optimal date suggestions based on weather, crowds, and wildlife viewing

## Project Structure

```
frontend/             # React frontend application
src/                  # Backend FastAPI application
  agents/             # LangChain declarative agents
  models/             # Data models
  services/           # Application services
  tools/              # Agent tools for different capabilities
infrastructure/       # Azure deployment templates
```

## Local Development Setup

### Environment Variables

For local development, you'll need to set up your API keys in a `.keys` file in the root directory. This file is ignored by git to prevent accidental exposure of your credentials.

1. Make sure the `.keys` file has the following entries:

```
# Azure OpenAI keys
AZURE_OPENAI_API_KEY=your_azure_openai_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o
OPENAI_API_VERSION=2023-05-15

# Weather API (RapidAPI - Open Weather)
WEATHER_API_KEY=your_rapidapi_key_here

# Other service keys
MAPS_API_KEY=your_maps_api_key_here
RESTAURANT_API_KEY=your_restaurant_api_key_here

# Security keys
JWT_SECRET_KEY=a_random_secret_key_for_local_development_only

# Database connection strings
COSMOS_DB_CONNECTION_STRING=your_cosmos_db_connection_string_here
```

2. Replace the placeholder values with your actual API keys:

- Get an Azure OpenAI API key from the Azure portal
- Get a RapidAPI key and subscribe to the Open Weather API at https://rapidapi.com/worldapi/api/open-weather13/
- For local testing, the JWT_SECRET_KEY can be any random string

### Backend Setup

1. Create a Python virtual environment:

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On macOS/Linux
```

2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Run the FastAPI application:

```bash
cd src
python app.py
```

The backend will be available at http://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install the required packages:

```bash
npm install
```

3. Run the React development server:

```bash
npm start
```

The frontend will be available at http://localhost:3000

## Deployment

The application can be deployed to Azure using the Bicep template in the infrastructure directory.

```bash
az login
az deployment group create --resource-group YourResourceGroup --template-file infrastructure/main.bicep
```

## License

[MIT](LICENSE)

#!/bin/bash

# Exit on error
set -e

# Variables
RESOURCE_GROUP="AgenticTravel"
LOCATION="eastus"
APP_NAME="yellowstone-trip-planner"
ENVIRONMENT="dev"

# Login to Azure
echo "Logging into Azure..."
az login

# Create Resource Group
echo "Creating resource group: $RESOURCE_GROUP..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Deploy Bicep template
echo "Deploying Azure resources using Bicep..."
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file infrastructure/main.bicep \
  --parameters location=$LOCATION appName=$APP_NAME environment=$ENVIRONMENT

# Install Python dependencies
echo "Installing Python dependencies..."
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Output success message
echo "Setup completed successfully!"

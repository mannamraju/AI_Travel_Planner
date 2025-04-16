#!/bin/bash

# Exit on error
set -e

# Variables
RESOURCE_GROUP="AgentTravel"
LOCATION="westus2"
APP_NAME="trip-plan"
ENVIRONMENT="dev"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
if [[ "$PYTHON_VERSION" =~ ^3\.12 ]]; then
  echo "Error: Python 3.12 detected. Please use Python 3.11 for compatibility with aiohttp."
  exit 1
fi

# Prompt user for action
echo "Select an option:"
echo "1. Deploy Azure resources"
echo "2. Install Python dependencies"
read -p "Enter your choice (1 or 2): " choice

if [[ "$choice" == "1" ]]; then
  # Check if Azure session is active
  echo "Checking Azure session..."
  if ! az account show > /dev/null 2>&1; then
    echo "No active Azure session found. Logging into Azure..."
    az login
  else
    echo "Azure session is already active."
  fi

  # Create Resource Group
  echo "Creating resource group: $RESOURCE_GROUP..."
  az group create --name $RESOURCE_GROUP --location $LOCATION

  # Deploy Bicep template
  echo "Deploying Azure resources using Bicep..."
  az deployment group create \
    --resource-group $RESOURCE_GROUP \
    --template-file infrastructure/main.bicep \
    --parameters location=$LOCATION appName=$APP_NAME environment=$ENVIRONMENT

elif [[ "$choice" == "2" ]]; then
  # Install Python dependencies
  echo "Installing Python dependencies..."
  python3 -m venv venv
  source venv/bin/activate
  pip3 install --upgrade pip setuptools wheel
  pip3 install aiohttp --only-binary :all:
  pip3 install -r requirements.txt

else
  echo "Invalid choice. Exiting."
  exit 1
fi

# Output success message
echo "Setup completed successfully!"

#!/bin/bash

# This script will set up the React app in the /web directory and then return to the main directory

# Save the current directory
MAIN_DIR=$(pwd)

# Navigate into the /web directory
cd web || exit

# Check if npm is installed
if ! command -v npm &> /dev/null
then
    echo "npm could not be found. Please install it to continue."
    exit 1
fi

# Install dependencies using npm
echo "Installing dependencies..."
npm install

# Optionally, you can also build the app
# echo "Building the app..."
# npm run build

# Return to the main directory
cd "$MAIN_DIR" || exit

echo "Setup complete. Dependencies installed, and returned to main directory."
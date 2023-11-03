#!/bin/bash

# Save the current directory
MAIN_DIR=$(pwd)

# Navigate to the web directory where the React app is located
cd web

# Check if npm is installed
if ! command -v npm &> /dev/null
then
    echo "npm could not be found, please install it first."
    exit 1
fi

# Install npm dependencies and build the project
echo "Installing npm dependencies..."
npm install

echo "Building the React app..."
npm run build

# Check if the build directory exists after the build process
if [ -d "build" ]; then
    # Check if deploy/web directory exists; create it if it doesn't
    if [ ! -d "../deploy/web" ]; then
        mkdir -p ../deploy/web
    fi

    # Copy the build directory to the deploy/web directory
    echo "Copying build directory to deploy/web..."
    cp -R build/* ../deploy/web/

    echo "The React app has been built and copied to deploy/web."
else
    echo "Build directory not found. The build process might have failed."
    exit 1
fi

# Return to the original directory
cd "$MAIN_DIR"
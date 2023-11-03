#!/bin/bash

# This script will create a virtual environment for the project using Python 3.10

# Define the environment name
VENV_NAME="venv"

# Check if Python 3.10 is installed
if ! command -v python3.10 &> /dev/null
then
    echo "Python 3.10 could not be found, please install it first."
    exit 1
fi

# Create virtual environment
python3.10 -m venv $VENV_NAME

# Activate virtual environment
source $VENV_NAME/bin/activate

# Upgrade pip to the latest version
pip install --upgrade pip

# Check if requirements.txt exists and install dependencies
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "requirements.txt not found, skipping dependency installation."
fi

echo "Virtual environment setup complete. Type 'source $VENV_NAME/bin/activate' to activate it."

echo "Downloading nltk data..."

# Activate virtual environment
source $VENV_NAME/bin/activate

# Function to download NLTK data
download_nltk_data() {
    python -m nltk.downloader stopwords
    python -m nltk.downloader punkt
    python -m nltk.downloader wordnet
}

download_nltk_data

echo "NLTK data downloaded."

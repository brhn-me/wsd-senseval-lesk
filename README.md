# Word Sense Disambiguation GUI

This project is a React-based web application for Word Sense Disambiguation (WSD).

## Project Folder Structure

Below is the outline of the project's directory and file structure:
```bash
wsd-senseval-lesk # Root folder of the project
│
├── app.py # Flask application entry point
│
├── wsd-app # React application (frontend)
│ ├── build # Compiled and minified production build
│ ├── public # Static files like HTML, icons, and manifest
│ ├── src # Source files for the React app
│ └── package.json # NPM package and script definitions
│
├── notebooks # Jupyter notebooks for all analysis and explorations
│ └── .ipynb files # Individual Jupyter notebooks
│
├── scripts # Python scripts
│ └── .py files # Standalone Python scripts for various tasks (mostly various implementation of lesk)
│
├── data # Data directory for CSV exports from our analysis and datasets
│ └── .csv files # CSV dataset files
│
└── screenshots # Screenshots of the app for documentation
```

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Before you begin, ensure you have met the following requirements:

* You have `node` and `npm` installed. You can download them from [here](https://nodejs.org/).
* You have Python and Flask installed if you're planning to run the backend server locally. Python can be downloaded from [here](https://www.python.org/downloads/), and Flask can be installed using pip.

### Installing

Follow these steps to get your development environment running:

1. Clone the repository:

```bash
git clone https://github.com/brhn-me/wsd-senseval-lesk.git
cd wsd-senseval-lesk
```

2. Install project dependencies:
```bash
npm install
```

3. (Optional) Set up your Python virtual environment and install Flask:
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install flask

## Configuration
To configure the Flask backend API:

(Optional) If your React app makes requests to a Flask API, update the API base URL in your React app's .env file or wherever you store your configuration:
```
REACT_APP_API_BASE_URL=http://localhost:5000/api
```
Set environment variables needed for Flask.

## Running the project
To run the project locally:

1. Start the React development server:
```bash
npm start
```
This command will start the React application and open it in your default web browser.

2. To run the Flask server, navigate to the server directory and run:
```bash
flask run
```
Your Flask API should now be serving requests at `http://localhost:5000/api`.

## Building for production
To create a production build of the React app, run:
```bash
npm run build
```
This command will create a build directory with all the production files.

## Serving the production build with Flask
To serve the production build files with Flask, ensure the Flask server is configured to serve the static files from the build directory:
```bash
from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='../wsd-app/build')

# ... existing Flask routes

if __name__ == '__main__':
    app.run(use_reloader=True, port=5000, threaded=True)
```

After configuration, run your Flask app, and it will serve your React app at the root endpoint.

## Running with Docker

This section covers the setup and deployment of the Word Sense Disambiguation GUI using Docker.

### Prerequisites

- Docker installed on your machine. Installation guides for Docker can be found [here](https://docs.docker.com/get-docker/).

### Building the Docker Image

To build the Docker image for the application, navigate to the root directory of the project where the `Dockerfile` is located and run the following command:

```bash
docker build -t wsd-app-image .
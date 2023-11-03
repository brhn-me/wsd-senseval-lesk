# Stage 1: Building the React application
FROM node:latest as build-stage
WORKDIR /app
COPY web/package*.json /app/
RUN npm install
COPY web/ /app/
RUN npm run build

# Stage 2: Setting up the Flask application
FROM python:3.10
WORKDIR /code

# Install Python dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy built React app from the previous stage
COPY --from=build-stage /app/build /code/web/build

# Copy Flask application to Docker image
COPY . /code/

# Expose the port the app runs on
EXPOSE 5000

# Set environment variable to serve React's build folder as static files
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# Start Flask app
CMD ["flask", "run"]


# Build your Docker image
# docker build -t web-image .

# Run your Docker container
# docker run -p 5000:5000 web-image

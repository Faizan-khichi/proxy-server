# Use an official lightweight Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy your Python script and requirements file into the container
COPY requirements.txt .
COPY server.py .

# Expose the port the app runs on (Fly.io will handle the mapping)
EXPOSE 8080

# The command to run your Python script when the container starts
CMD ["python", "server.py"]

# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files, including the SQLite database
COPY . .

# Expose the port your app runs on
EXPOSE 5000

# Define the command to run your application
CMD ["python", "main.py"]
# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application files into the container
COPY . .

# Install necessary packages
RUN pip install --no-cache-dir -r requirements.txt

# Start the FastAPI application on port 5000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
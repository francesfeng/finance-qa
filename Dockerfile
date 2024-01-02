# Use an official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.10-slim

# Set environment variables. PYTHONUNBUFFERED ensures our console output looks familiar and is not buffered by Docker, which is useful for debugging.
ENV PYTHONUNBUFFERED True

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Inform Docker that the container listens on the specified network ports at runtime. 80 is standard for HTTP.
EXPOSE 80

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

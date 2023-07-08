# https://hub.docker.com/_/python
#FROM python:3.10-slim-bullseye
# FROM python:3.10

# ENV PYTHONUNBUFFERED True
# ENV APP_HOME /app
# WORKDIR $APP_HOME
# COPY . ./

# RUN pip install --no-cache-dir -r requirements.txt

# WORKDIR /code
# COPY ./requirements.txt /code/requirements.txt
# RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
# COPY ./app /code/app

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]


# Use a slim Python base image
FROM python:3.10-slim-bullseye

# Create a dedicated directory for your app
WORKDIR /code

# Copy the requirements file into the Docker image
COPY ./requirements.txt /code/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the rest of the application into the Docker image
COPY ./app /code/app

# Indicate that the application listens on port 8080
EXPOSE 8080

# Specify a non-root user to run the application
RUN useradd -m myuser
USER myuser

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]

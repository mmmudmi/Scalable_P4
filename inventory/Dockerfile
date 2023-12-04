# Use the official Python image as the base image
FROM python:3.11
# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY ./requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY ./inventory/ ./

CMD ["celery", "-A", "main.celery", "worker", "-E", "--pool=solo", "--loglevel=info", "-Q", "inventory"]
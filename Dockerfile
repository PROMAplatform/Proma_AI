# Use an official Python runtime as a parent image
FROM python:3.11.5

# Set environment variables for Docker
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port 8000 to allow external connections to this port
EXPOSE 8000

# Define the command to run on container start
CMD ["python", "proma/manage.py", "runserver", "0.0.0.0:8000"]
# Use an official Python runtime as the base image
FROM python:3.12

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    iputils-ping \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
# Copy the Django project into the container
COPY . /app/
WORKDIR /app/
RUN chmod +x entrypoint.sh
# Expose the port the app runs on
EXPOSE 8000
# Command to run the application
# CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "core.asgi:application"]
# ENTRYPOINT ["entrypoint.sh"]
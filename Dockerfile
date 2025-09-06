# Use Python 3.11 slim
FROM python:3.11-slim

# Set working directory
WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
ENV FLASK_APP=app.py

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 5000

# Start the Flask app
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"] 
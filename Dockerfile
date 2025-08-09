# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy ALL application files
COPY . .

# Create necessary directories and set proper permissions
RUN mkdir -p /app/static/pictures \
    /app/static/target_person_pictures \
    /app/static/comparison_pictures \
    /app/assets \
    /app/logs \
    /app/templates \
    /app/data/static/pictures \
    /app/data/static/target_person_pictures \
    /app/data/static/comparison_pictures \
    /app/data/logs

# Set permissions - THIS IS THE KEY FIX
RUN chmod -R 777 /app/static \
    && chmod -R 777 /app/logs \
    && chmod -R 777 /app/data \
    && chmod +x /app/*.py

# Don't create non-root user - run as root to avoid permission issues
# USER appuser

# Expose port for dashboard
EXPOSE 5000

# Default command
CMD ["python", "new_main.py"]
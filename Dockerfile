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

# Copy application code
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/static/pictures \
    /app/static/target_person_pictures \
    /app/static/comparison_pictures \
    /app/assets \
    /app/logs \
    /app/templates \
    && chmod -R 755 /app/static \
    && chmod -R 755 /app/logs

# Create a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port for dashboard
EXPOSE 5000

# Default command (can be overridden in docker-compose)
CMD ["python", "new_main.py"]
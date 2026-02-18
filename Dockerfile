FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN python3 -m venv .venv && . .venv/bin/activate

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 5010

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5010", "--workers", "4", "--timeout", "120", "wsgi:app"]

FROM python:3.11-slim

# Prevent Python buffering
ENV PYTHONUNBUFFERED=1
ENV PORT=10000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    curl \
    rustc \
    cargo \
    git \
    && rm -rf /var/lib/apt/lists/*
    
WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .
# Create downloads directory
RUN mkdir -p downloads

# Render uses port 10000
EXPOSE 10000

# Start Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "1", "--timeout", "600", "app:app"]

# Use lightweight base image
FROM python:3.10-slim

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies (needed for torch & sentence-transformers)
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip first (important)
RUN pip install --upgrade pip

# Install PyTorch separately (much faster + reliable)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Copy requirements first (to enable Docker caching)
COPY requirements.txt .

# Install remaining dependencies
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

# Copy project files
COPY . .

# Expose Gradio port
EXPOSE 7860

# Start application
CMD ["python", "app.py"]
FROM python:3.11-slim

# Prevents Python from writing .pyc files and enables unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

WORKDIR /app

# Install build essentials for any dependencies that may require compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	&& rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY app /app

# Expose the port used by the application
EXPOSE 80

# Use gunicorn with 2 workers for FastAPI app
# If you need uvicorn workers for async, use: -k uvicorn.workers.UvicornWorker
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:80", "main:app", "-k", "uvicorn.workers.UvicornWorker"]
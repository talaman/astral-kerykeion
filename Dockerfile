FROM python:3.14-slim

# Prevents Python from writing .pyc files and enables unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	TMPDIR=/tmp \
	CHART_OUTPUT_DIR=/tmp/astral-kerykeion/output \
	HOME=/tmp \
	XDG_CACHE_HOME=/tmp \
	XDG_CONFIG_HOME=/tmp

WORKDIR /app

RUN groupadd --system --gid 10001 appuser \
	&& useradd --system --uid 10001 --gid 10001 --create-home appuser

# Install build essentials for any dependencies that may require compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	&& rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY app /app
RUN mkdir -p /tmp/astral-kerykeion/output \
	&& chown -R appuser:appuser /app /tmp/astral-kerykeion /home/appuser

# Expose the port used by the application
EXPOSE 8000

USER appuser

# Use gunicorn with 2 workers for FastAPI app
# If you need uvicorn workers for async, use: -k uvicorn.workers.UvicornWorker
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "main:app", "-k", "uvicorn.workers.UvicornWorker"]

FROM python:3.13.7-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install build dependencies 
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install Python dependencies
COPY app/requirements.txt .
RUN uv pip install --no-cache-dir -r requirements.txt --system

# Copy project
COPY app/ .

# Expose port
EXPOSE 8000

# Use the entrypoint script
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
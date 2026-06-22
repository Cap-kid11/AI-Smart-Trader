# Production image for the Veridian API.
FROM python:3.12-slim

# Don't write .pyc files; flush logs immediately.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install deps first for better layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code.
COPY . .

# The platform provides $PORT; default to 8000 locally.
ENV PORT=8000
EXPOSE 8000

# Start the API. Uses the shell form so $PORT expands at runtime.
CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT}

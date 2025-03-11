FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install specific dependencies needed for your application
RUN pip install --no-cache-dir fastapi uvicorn opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi

# Disable OpenTelemetry tracing to avoid connection errors
ENV OTEL_TRACES_EXPORTER=none

# Copy application code
COPY . .

# Define environment variables for the LLM service
ENV LLM_SERVICE_HOST_IP="localhost"
ENV LLM_SERVICE_PORT=8080

# Expose the port your application runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "chat.py"]

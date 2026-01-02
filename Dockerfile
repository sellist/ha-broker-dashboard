FROM python:3.14-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy application code
COPY ha_broker_dashboard/ ./ha_broker_dashboard/
COPY config.yaml .

# Expose the dashboard port
EXPOSE 8080

# Run the dashboard
CMD ["python", "-m", "ha_broker_dashboard.main"]


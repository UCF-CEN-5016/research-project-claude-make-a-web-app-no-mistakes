# Multi-stage Dockerfile for AgentSpec
# Builds a container with Python 3.12 and Java 17 for full testing capabilities

# Stage 1: Builder
FROM python:3.12-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Runtime
FROM python:3.12-slim

# Install runtime dependencies including Java for ANTLR
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-21-jre-headless \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app:$PYTHONPATH

# Set working directory
WORKDIR /app

# Copy entire project (build context is AgentSpec/)
COPY . /app

# Install Python dependencies
# Use requirement.txt if available, otherwise use pyproject.toml
RUN if [ -f "requirement.txt" ]; then \
        pip install --no-cache-dir -r requirement.txt; \
    else \
        pip install --no-cache-dir -e .; \
    fi

# Make the run script executable
RUN chmod +x src/run.sh

# Set entrypoint to the bash script
ENTRYPOINT ["bash", "src/run.sh"]

# Default command (can be overridden)
CMD []

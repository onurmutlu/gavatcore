# 🚀 GAVATCore v6.0 OnlyVips - Production Dockerfile
# Multi-stage build for optimized production image

# Build stage
FROM python:3.13-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VERSION="6.0.0"
ARG VCS_REF

# Labels for container metadata
LABEL maintainer="GAVATCore Team" \
      version="${VERSION}" \
      description="GAVATCore OnlyVips Platform - Production Ready" \
      build-date="${BUILD_DATE}" \
      vcs-ref="${VCS_REF}"

# Set working directory
WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements*.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.13-slim as production

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN groupadd -r gavatcore && useradd -r -g gavatcore gavatcore

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs sessions data/analytics data/personas data/profiles \
    && chown -R gavatcore:gavatcore /app

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_ENV=production \
    FLASK_DEBUG=0

# Expose ports
EXPOSE 5050 5051 5055

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5050/api/system/status || exit 1

# Switch to non-root user
USER gavatcore

# Default command
CMD ["python3", "run.py"]
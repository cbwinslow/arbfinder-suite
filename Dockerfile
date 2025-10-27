# Build stage for frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code
COPY backend/ ./backend/
COPY pyproject.toml ./

# Install the package
RUN pip install -e .

# Copy built frontend
COPY --from=frontend-builder /app/frontend/.next ./frontend/.next
COPY --from=frontend-builder /app/frontend/public ./frontend/public
COPY --from=frontend-builder /app/frontend/package*.json ./frontend/
RUN cd frontend && npm ci --production

# Expose ports
EXPOSE 8080 3000

# Environment variables
ENV ARBF_DB=/data/arb_finder.sqlite3
ENV PYTHONUNBUFFERED=1

# Create data directory
RUN mkdir -p /data

# Volume for persistent data
VOLUME ["/data"]

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/ || exit 1

# Start script
COPY start.sh /app/
RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]

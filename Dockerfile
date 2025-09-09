# Multi-stage build for minimal final image
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy source code
COPY . .

# Install the package
RUN pip install --no-cache-dir --user .

# Final stage - minimal runtime image
FROM kasmweb/core-ubuntu-focal:latest

# Install Python runtime
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-minimal \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash mcp-user

# Set up Python path
ENV PYTHONPATH=/home/mcp-user/.local/lib/python3.11/site-packages:$PYTHONPATH
ENV PATH=/home/mcp-user/.local/bin:$PATH

# Copy installed packages from builder
COPY --from=builder --chown=mcp-user:mcp-user /root/.local /home/mcp-user/.local

# Set working directory
WORKDIR /home/mcp-user/app

# Copy application files
COPY --chown=mcp-user:mcp-user src/ ./src/
COPY --chown=mcp-user:mcp-user setup.py README.md requirements.txt ./

# Switch to non-root user
USER mcp-user

# Expose MCP server port (for HTTP+SSE transport)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import socket; s = socket.socket(); s.connect(('localhost', 8080)); s.close()"

# Set environment variables (can be overridden at runtime)
ENV MCP_SERVER_PORT=8080
ENV MCP_SERVER_HOST=0.0.0.0
ENV LOG_LEVEL=INFO

# Entry point
ENTRYPOINT ["python3", "-m", "src"]

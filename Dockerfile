FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all MCP servers
COPY docs-mcp/ ./docs-mcp/
COPY personas-mcp/ ./personas-mcp/
COPY coderef-mcp/ ./coderef-mcp/

# Set working directory to docs-mcp for the HTTP server
WORKDIR /app/docs-mcp

# Expose port (Railway sets PORT env var)
EXPOSE 5000

# Start command - Railway will override PORT
CMD ["sh", "-c", "gunicorn http_server:app --bind 0.0.0.0:${PORT:-5000} --timeout 300 --workers 2"]

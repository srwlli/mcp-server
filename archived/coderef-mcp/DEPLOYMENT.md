# CodeRef2 MCP Service - Deployment Guide

**Version:** 1.0.0
**Status:** Production Ready

---

## Quick Start (5 minutes)

### Minimal Setup

```bash
# 1. Clone/download service
cd coderef2-mcp

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run server
python server.py

# 4. Verify (in another terminal)
python -c "from server import get_server; import asyncio; \
s = get_server(); print(asyncio.run(s.health_check()))"
```

### Expected Output

```json
{
  "status": "healthy",
  "service": "coderef2-mcp",
  "version": "1.0.0",
  "tools_available": 6,
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

---

## System Requirements

### Minimum

- Python 3.10+
- 256 MB RAM
- 50 MB disk space

### Recommended

- Python 3.11+
- 512 MB RAM
- 100 MB disk space
- Linux or macOS (Windows supported but use WSL2)

### Dependencies

See `requirements.txt`:

```
mcp>=1.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-json-logger>=2.0.0
```

---

## Installation Methods

### Method 1: Direct Installation

```bash
# Clone/download
git clone https://github.com/.../coderef2-mcp.git
cd coderef2-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -m pytest tests/unit/ -q  # Run quick unit tests
```

### Method 2: Poetry

```bash
# Install Poetry if needed
curl -sSL https://install.python-poetry.org | python3 -

# Install with Poetry
poetry install

# Activate environment
poetry shell

# Run tests
poetry run pytest tests/ -q
```

### Method 3: Docker

```bash
# Build image
docker build -t coderef2-mcp:1.0.0 .

# Run container
docker run -d \
  --name coderef2-mcp \
  -p 8000:8000 \
  -e CODEREF_LOG_LEVEL=INFO \
  coderef2-mcp:1.0.0

# Check logs
docker logs coderef2-mcp

# Health check
docker exec coderef2-mcp python -c "from server import get_server; \
import asyncio; s = get_server(); print(asyncio.run(s.health_check()))"
```

### Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV CODEREF_LOG_LEVEL=INFO
ENV PYTHONUNBUFFERED=1

CMD ["python", "server.py"]
```

---

## Configuration

### Environment Variables

```bash
# Logging
export CODEREF_LOG_LEVEL=INFO               # DEBUG, INFO, WARNING, ERROR
export CODEREF_LOG_FORMAT=json              # json or text

# Service
export CODEREF_SERVICE_NAME=coderef2-mcp
export CODEREF_SERVICE_VERSION=1.0.0

# Performance
export CODEREF_BATCH_WORKERS=5              # Max parallel workers
export CODEREF_BATCH_TIMEOUT_MS=5000        # Batch timeout

# Integration
export CODEREF_DOCS_SERVICE_URL=http://localhost:5000  # docs-mcp location
export CODEREF_DOCS_FALLBACK_ENABLED=true   # Fallback mode
```

### Configuration Files

1. **constants.py** - Service constants and type definitions
2. **logger_config.py** - Logging configuration
3. **.env** - Environment-specific settings (optional)

---

## Deployment Scenarios

### Scenario 1: Local Development

```bash
# Simple setup for development/testing
python server.py

# Output:
# CodeRef2 MCP server module loaded
# Service: coderef2-mcp v1.0.0
# Tools available: 6
```

**Typical:**
- Direct Python execution
- File-based storage
- No persistence layer needed

---

### Scenario 2: Production on Linux

```bash
# 1. Install to standard location
sudo mkdir -p /opt/coderef2-mcp
sudo cp -r . /opt/coderef2-mcp/

# 2. Setup systemd service
sudo cat > /etc/systemd/system/coderef2-mcp.service <<EOF
[Unit]
Description=CodeRef2 MCP Service
After=network.target

[Service]
Type=simple
User=coderef
WorkingDirectory=/opt/coderef2-mcp
Environment="PATH=/opt/coderef2-mcp/venv/bin"
Environment="CODEREF_LOG_LEVEL=INFO"
ExecStart=/opt/coderef2-mcp/venv/bin/python server.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 3. Enable and start
sudo systemctl daemon-reload
sudo systemctl enable coderef2-mcp
sudo systemctl start coderef2-mcp

# 4. Check status
sudo systemctl status coderef2-mcp

# 5. View logs
sudo journalctl -u coderef2-mcp -f
```

**Production Considerations:**
- Run as dedicated user (`coderef`)
- Use systemd for process management
- Enable log aggregation
- Setup monitoring/alerting

---

### Scenario 3: Docker Compose (Multi-Service)

```bash
# docker-compose.yml
version: '3.8'

services:
  # Other services...
  docs-mcp:
    image: docs-mcp:1.0.0
    ports:
      - "5000:5000"
    environment:
      LOG_LEVEL: INFO

  coderef2-mcp:
    build: .
    depends_on:
      - docs-mcp
    environment:
      CODEREF_LOG_LEVEL: INFO
      CODEREF_DOCS_SERVICE_URL: http://docs-mcp:5000
    ports:
      - "8000:8000"
```

```bash
# Deploy
docker-compose up -d

# Check services
docker-compose ps

# View logs
docker-compose logs -f coderef2-mcp
```

---

### Scenario 4: Kubernetes Deployment

Create `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: coderef2-mcp
  labels:
    app: coderef2-mcp
spec:
  replicas: 2
  selector:
    matchLabels:
      app: coderef2-mcp
  template:
    metadata:
      labels:
        app: coderef2-mcp
    spec:
      containers:
      - name: coderef2-mcp
        image: coderef2-mcp:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: CODEREF_LOG_LEVEL
          value: "INFO"
        - name: CODEREF_DOCS_SERVICE_URL
          value: "http://docs-mcp:5000"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          exec:
            command:
            - python
            - -c
            - "from server import get_server; import asyncio; s = get_server(); asyncio.run(s.health_check())"
          initialDelaySeconds: 10
          periodSeconds: 30
---
apiVersion: v1
kind: Service
metadata:
  name: coderef2-mcp
spec:
  selector:
    app: coderef2-mcp
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: ClusterIP
```

```bash
# Deploy to Kubernetes
kubectl apply -f k8s-deployment.yaml

# Check deployment
kubectl get deployment coderef2-mcp

# View logs
kubectl logs -f deployment/coderef2-mcp
```

---

## Pre-Deployment Checklist

### Code Quality
- [ ] All tests passing: `pytest tests/ -v`
- [ ] No type errors: `mypy coderef2/ --ignore-missing-imports`
- [ ] Code style compliant: `black --check .`

### Functionality
- [ ] Health check passing
- [ ] All 6 tools registered
- [ ] Query tool working
- [ ] Analyze tool working
- [ ] Validation tools working
- [ ] Batch processing working

### Performance
- [ ] Query < 500ms on 100 elements
- [ ] Analyze < 500ms
- [ ] Validation < 200ms per element
- [ ] Batch validation < 5s for 100 items

### Security
- [ ] No hardcoded credentials
- [ ] Environment variables used for config
- [ ] Logging doesn't expose sensitive data
- [ ] Dependencies up to date: `pip list --outdated`

### Documentation
- [ ] README complete
- [ ] API documentation accurate
- [ ] Examples runnable
- [ ] Deployment guide complete

---

## Post-Deployment Verification

### Immediate Checks (First 5 minutes)

```bash
# 1. Service running
systemctl status coderef2-mcp

# 2. Port listening
netstat -tlnp | grep 8000

# 3. Health check
curl http://localhost:8000/health

# 4. Logs clean
journalctl -u coderef2-mcp -n 20
```

### Functional Tests (First hour)

```bash
# Run integration tests against deployed service
pytest tests/integration/ -v -k "test_query"

# Test each tool
python -m pytest tests/unit/test_query_tools.py::TestQueryEngine::test_query_by_reference -v
python -m pytest tests/unit/test_analysis_tools.py::TestDeepAnalysisEngine -v
python -m pytest tests/unit/test_validation_tools.py::TestReferenceValidator -v
```

### Performance Validation (First day)

```bash
# Run performance suite
pytest tests/performance/ -v

# Sample query performance
time python -c "from server import CodeRef2Server; import asyncio; \
s = CodeRef2Server(); asyncio.run(s._handle_call_tool('mcp__coderef__query', {'query': '@Fn/src/*'}))"
```

---

## Monitoring & Logging

### Log Format

JSON logs with structure:

```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "level": "INFO",
  "name": "server",
  "message": "Query tool invoked",
  "extra": {
    "tool": "mcp__coderef__query",
    "execution_time_ms": 245.3
  }
}
```

### Log Levels

- `DEBUG` - Detailed development information
- `INFO` - Normal operations
- `WARNING` - Potential issues
- `ERROR` - Error conditions
- `CRITICAL` - System critical

### Monitoring Metrics

**Key metrics to monitor:**

1. **Request Volume**
   ```
   requests_per_second
   requests_per_minute
   ```

2. **Performance**
   ```
   query_time_ms (avg, p50, p99)
   analyze_time_ms
   validate_time_ms
   ```

3. **Success Rate**
   ```
   tool_success_rate_percentage
   query_success_rate
   validation_error_rate
   ```

4. **Resource Usage**
   ```
   memory_mb
   cpu_percent
   open_connections
   ```

### Alerting Rules

```yaml
alerts:
  - name: ServiceDown
    condition: health_check_failed
    threshold: 2_consecutive_failures
    action: page_oncall

  - name: HighLatency
    condition: p99_latency_ms > 1000
    threshold: 5_minutes
    action: notify_slack

  - name: HighErrorRate
    condition: error_rate > 5%
    threshold: 10_minutes
    action: notify_slack

  - name: HighMemory
    condition: memory_percent > 80%
    threshold: 5_minutes
    action: page_oncall
```

---

## Troubleshooting

### Issue: Service won't start

**Symptoms:** Port already in use or import errors

**Solutions:**
```bash
# Check port availability
lsof -i :8000
ss -tlnp | grep 8000

# Kill conflicting process
kill -9 <PID>

# Check for import errors
python -c "from server import create_server; print('Import OK')"

# Check Python version
python --version  # Must be 3.10+
```

### Issue: Slow queries

**Symptoms:** Query taking > 500ms

**Solutions:**
```bash
# Add debug logging
CODEREF_LOG_LEVEL=DEBUG python server.py

# Profile the code
python -m cProfile -s cumulative test_query.py

# Check baseline dataset size
python -c "from tests.integration.test_fixtures import BaselineElementDataset; \
d = BaselineElementDataset(); print(d.get_stats())"
```

### Issue: Memory leak

**Symptoms:** Memory usage increasing over time

**Solutions:**
```bash
# Monitor memory
watch -n 1 'ps aux | grep server.py'

# Force garbage collection
python -c "import gc; gc.collect(); print('GC done')"

# Use memory profiler
pip install memory-profiler
python -m memory_profiler server.py
```

### Issue: High CPU usage

**Symptoms:** CPU at 100% with normal load

**Solutions:**
```bash
# Check running processes
top -p <PID>

# Reduce batch workers
export CODEREF_BATCH_WORKERS=2

# Enable performance profiling
python -m cProfile server.py
```

---

## Upgrading

### Version Upgrade Process

```bash
# 1. Backup current installation
cp -r coderef2-mcp coderef2-mcp.backup

# 2. Download new version
git pull origin main
# or download new release

# 3. Stop service
sudo systemctl stop coderef2-mcp

# 4. Install dependencies
pip install -r requirements.txt --upgrade

# 5. Run migration/tests
pytest tests/ -v

# 6. Start service
sudo systemctl start coderef2-mcp

# 7. Verify
sudo systemctl status coderef2-mcp
curl http://localhost:8000/health
```

### Rollback

```bash
# If issues arise
sudo systemctl stop coderef2-mcp
rm -rf coderef2-mcp
mv coderef2-mcp.backup coderef2-mcp
sudo systemctl start coderef2-mcp
```

---

## Scaling

### Horizontal Scaling

For multiple instances, use load balancer:

```nginx
upstream coderef2_backend {
    server 127.0.0.1:8000 max_fails=2 fail_timeout=30s;
    server 127.0.0.1:8001 max_fails=2 fail_timeout=30s;
    server 127.0.0.1:8002 max_fails=2 fail_timeout=30s;
}

server {
    listen 80;
    server_name api.coderef2.local;

    location / {
        proxy_pass http://coderef2_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_connect_timeout 10s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    location /health {
        proxy_pass http://coderef2_backend;
        access_log off;
    }
}
```

### Vertical Scaling

For single instance performance:

```bash
# Increase workers
export CODEREF_BATCH_WORKERS=20

# Increase memory allocation
export PYTHONUNBUFFERED=1

# Use PyPy for better performance
pypy3 server.py
```

---

## Maintenance

### Regular Tasks

**Daily:**
- [ ] Monitor logs for errors
- [ ] Check health endpoint
- [ ] Verify performance metrics

**Weekly:**
- [ ] Check for dependency updates
- [ ] Review error logs
- [ ] Backup configuration

**Monthly:**
- [ ] Update dependencies: `pip list --outdated`
- [ ] Run full test suite
- [ ] Performance review
- [ ] Security audit

### Backup Strategy

```bash
# Backup configuration
tar -czf coderef2-config-$(date +%Y%m%d).tar.gz \
  constants.py logger_config.py

# Backup data (if applicable)
tar -czf coderef2-data-$(date +%Y%m%d).tar.gz \
  data/ cache/

# Rotate backups
find backups/ -name "coderef2-*.tar.gz" -mtime +30 -delete
```

---

## Support & Troubleshooting

**Documentation:**
- README.md - Overview and quick start
- API.md - Tool specifications
- This file - Deployment guide

**Common Issues:**
- Service won't start → Check Python version, dependencies
- Slow performance → Check system resources, enable DEBUG logging
- Connection errors → Verify network, firewall rules

**Getting Help:**
- Check test files for usage examples
- Review logs with `CODEREF_LOG_LEVEL=DEBUG`
- Run tests: `pytest tests/ -v -s`

---

**Version:** 1.0.0
**Last Updated:** Phase 6 Implementation Complete
**Status:** Production Ready

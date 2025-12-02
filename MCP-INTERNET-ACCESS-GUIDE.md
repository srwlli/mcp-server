# MCP Server Internet Access - Comprehensive Research Report

## Executive Summary

This document provides comprehensive research on exposing MCP servers over the internet, covering transport protocols, deployment platforms, authentication methods, and security best practices.

**Current State**: Your 3 MCP servers (docs-mcp, personas-mcp, coderef-mcp) use STDIO transport (local only). You have an existing `http_server.py` in docs-mcp that provides HTTP wrapper but **lacks authentication**.

---

## 1. MCP Transport Protocols

### Official MCP Transports

| Transport | Status | Use Case | Bidirectional |
|-----------|--------|----------|---------------|
| **STDIO** | Standard | Local process communication | Yes |
| **Streamable HTTP** | Recommended | Remote access (modern) | Yes (via SSE) |
| **SSE** | Deprecated | Remote access (legacy) | Partial |
| **WebSocket** | Proposed | Real-time applications | Yes |

### Transport Comparison

**STDIO (Current)**
- Pros: Native, no network overhead, secure by default
- Cons: Local only, no remote access
- Use when: Claude Code, Claude Desktop local usage

**Streamable HTTP (Recommended for Remote)**
- Pros: Modern standard, HTTP/2 compatible, firewall-friendly
- Cons: Requires HTTP server wrapper
- Use when: Remote access, CI/CD, ChatGPT integration
- Spec: `POST /mcp` with optional SSE for server-to-client streaming

**SSE (Server-Sent Events)**
- Pros: Simple, well-supported
- Cons: Deprecated in MCP spec, one-way streaming
- Use when: Legacy compatibility only

---

## 2. Deployment Platform Options

### Option A: Railway (Partially Configured)

**Already in your codebase**: `http_server.py` has `STANDALONE_MODE` for Railway

| Aspect | Details |
|--------|---------|
| **Pros** | Simple PaaS, auto-deploy from Git, free tier available |
| **Cons** | Limited free tier (500 hours/month), cold starts |
| **Cost** | Free tier, then $5/month base + usage |
| **Setup** | Push to Git, Railway auto-deploys |
| **SSL** | Automatic HTTPS via `*.up.railway.app` |
| **Auth** | Must implement yourself |

```bash
# Deploy to Railway
railway login
railway link
railway up
# Set env: STANDALONE_MODE=true
```

### Option B: Cloudflare Workers

| Aspect | Details |
|--------|---------|
| **Pros** | Edge deployment, built-in DDoS, 100k free req/day |
| **Cons** | Requires code rewrite (Workers runtime), no Python |
| **Cost** | Free tier generous, then $5/month |
| **Setup** | Requires TypeScript/JavaScript rewrite |
| **SSL** | Automatic HTTPS |
| **Auth** | Cloudflare Access, API tokens, mTLS |

**Best for**: High availability, global distribution, built-in security

### Option C: AWS (Lambda + API Gateway)

| Aspect | Details |
|--------|---------|
| **Pros** | Enterprise-grade, IAM integration, scales infinitely |
| **Cons** | Complex setup, cold starts, cost can grow |
| **Cost** | Pay-per-use, ~$0.20/million requests |
| **Setup** | SAM/CDK/Serverless Framework |
| **SSL** | ACM certificates (free) |
| **Auth** | IAM, Cognito, API keys, Lambda authorizers |

```yaml
# serverless.yml example
functions:
  mcp:
    handler: http_server.handler
    events:
      - http:
          path: /mcp
          method: post
```

### Option D: Google Cloud Run

| Aspect | Details |
|--------|---------|
| **Pros** | Container-based, auto-scaling, good Python support |
| **Cons** | Cold starts, requires Docker |
| **Cost** | Free tier (2M requests), then pay-per-use |
| **Setup** | Docker + `gcloud run deploy` |
| **SSL** | Automatic HTTPS |
| **Auth** | IAM, Cloud Identity, API keys |

**Recommended by Google for MCP**: [Secure Remote MCP on Google Cloud](https://cloud.google.com/blog/products/identity-security/how-to-secure-your-remote-mcp-server-on-google-cloud)

### Option E: Self-Hosted (VPS + Docker)

| Aspect | Details |
|--------|---------|
| **Pros** | Full control, no vendor lock-in, predictable cost |
| **Cons** | You manage everything (security, updates, scaling) |
| **Cost** | $5-20/month VPS (DigitalOcean, Linode, Hetzner) |
| **Setup** | Docker Compose + Nginx reverse proxy |
| **SSL** | Let's Encrypt (free) via Certbot |
| **Auth** | Implement yourself or use auth proxy (OAuth2-proxy, Authelia) |

```yaml
# docker-compose.yml
services:
  mcp:
    build: .
    ports:
      - "8080:5000"
  nginx:
    image: nginx
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/letsencrypt
```

### Option F: Use Existing Proxy/Gateway

**mcp-proxy** (sparfenyuk)
```bash
npx mcp-proxy --port 8080 -- python server.py
```

**supergateway** (supercorp-ai)
```bash
npx supergateway \
  --stdio "python server.py" \
  --outputTransport streamableHttp \
  --port 8000
```

**Pros**: No code changes, instant HTTP exposure
**Cons**: Additional dependency, may not support all features

---

## 3. Authentication Methods

### CRITICAL SECURITY WARNING

> **Research found ~1,862 internet-exposed MCP servers with nearly 100% lacking ANY authentication.** Never expose MCP servers without authentication.

### Option A: API Keys (Simple)

**How it works**: Shared secret in header (`X-API-Key: your-key`)

| Aspect | Details |
|--------|---------|
| **Pros** | Simple to implement, easy to revoke |
| **Cons** | Keys can leak, no user identity, no scopes |
| **Best for** | Personal use, internal tools, dev/test |
| **Implementation** | ~20 lines of code |

```python
# Flask middleware example
@app.before_request
def check_api_key():
    api_key = request.headers.get('X-API-Key')
    if api_key != os.environ.get('MCP_API_KEY'):
        return jsonify({'error': 'Unauthorized'}), 401
```

### Option B: OAuth 2.0 (Industry Standard)

**How it works**: Token-based auth with identity provider

| Aspect | Details |
|--------|---------|
| **Pros** | Industry standard, scoped access, user identity |
| **Cons** | Complex setup, requires IdP (Auth0, Okta, Keycloak) |
| **Best for** | Public APIs, multi-user, enterprise |
| **Flows** | Authorization Code + PKCE (recommended) |

**Providers**:
- **Auth0**: Easy setup, free tier (7k MAU)
- **Okta**: Enterprise-grade
- **Keycloak**: Self-hosted, open source
- **Google/GitHub OAuth**: Social login

```python
# Flask-JWT-Extended example
from flask_jwt_extended import jwt_required, get_jwt_identity

@app.route('/mcp', methods=['POST'])
@jwt_required()
def mcp_endpoint():
    current_user = get_jwt_identity()
    # ... handle MCP request
```

### Option C: mTLS (Mutual TLS)

**How it works**: Both client and server present certificates

| Aspect | Details |
|--------|---------|
| **Pros** | Strongest security, no passwords/tokens |
| **Cons** | Complex certificate management |
| **Best for** | Machine-to-machine, zero-trust networks |
| **Setup** | Generate CA, issue client certs |

### Option D: Cloudflare Access / Zero Trust

**How it works**: Cloudflare sits in front, handles auth

| Aspect | Details |
|--------|---------|
| **Pros** | No code changes, SSO integration, audit logs |
| **Cons** | Vendor lock-in, requires Cloudflare |
| **Best for** | Teams with existing Cloudflare |
| **Cost** | Free for up to 50 users |

### Option E: Basic Auth + HTTPS

**How it works**: Username:password in Authorization header

| Aspect | Details |
|--------|---------|
| **Pros** | Simple, universal support |
| **Cons** | Credentials in every request, no token expiry |
| **Best for** | Quick protection, internal tools |

### Authentication Comparison Matrix

| Method | Security | Complexity | Multi-User | Scopes | Best For |
|--------|----------|------------|------------|--------|----------|
| API Keys | Medium | Low | No | No | Personal/Dev |
| OAuth 2.0 | High | High | Yes | Yes | Public API |
| mTLS | Highest | Very High | Yes | No | Machine-to-Machine |
| Cloudflare Access | High | Low | Yes | Yes | Teams |
| Basic Auth | Low | Very Low | Limited | No | Quick Protection |

---

## 4. Security Best Practices

### Must-Have (Non-Negotiable)

1. **HTTPS Only** - Never HTTP for production
2. **Authentication** - At minimum API keys
3. **Rate Limiting** - Prevent abuse/DoS
4. **Input Validation** - Already in your code (validation.py)
5. **Audit Logging** - Log all access attempts

### Should-Have

1. **IP Allowlisting** - Restrict to known IPs
2. **Request Size Limits** - Prevent large payload attacks
3. **Timeout Limits** - Prevent long-running attacks
4. **CORS Configuration** - Restrict origins (current: `*` = dangerous)
5. **Secret Management** - Use env vars, not hardcoded

### Nice-to-Have

1. **WAF (Web Application Firewall)** - Block known attack patterns
2. **DDoS Protection** - Cloudflare, AWS Shield
3. **Penetration Testing** - Regular security audits
4. **Token Rotation** - Auto-expire and rotate credentials

### Your Current Security Gaps

| Gap | Risk | Fix |
|-----|------|-----|
| No authentication | Critical | Add API key at minimum |
| CORS = `*` | High | Restrict to specific origins |
| No rate limiting | Medium | Add Flask-Limiter |
| HTTP in dev | Medium | Enforce HTTPS |
| No audit logging | Medium | Add security event logging |

---

## 5. Architecture Options

### Architecture A: Direct HTTP Server (Current)

```
Internet → http_server.py (Flask) → MCP Tools
```

**Pros**: Simple, already built
**Cons**: Must implement all security yourself
**Effort**: Low (add auth to existing code)

### Architecture B: Reverse Proxy + HTTP Server

```
Internet → Nginx/Traefik → http_server.py → MCP Tools
                ↓
        (SSL termination, rate limiting)
```

**Pros**: SSL/auth at proxy level, defense in depth
**Cons**: Additional component to manage
**Effort**: Medium

### Architecture C: API Gateway + Serverless

```
Internet → API Gateway → Lambda/Cloud Run → MCP Tools
              ↓
    (Auth, rate limiting, monitoring)
```

**Pros**: Managed security, auto-scaling, pay-per-use
**Cons**: Vendor-specific, potential cold starts
**Effort**: High (repackaging required)

### Architecture D: Auth Proxy (OAuth2-Proxy/Authelia)

```
Internet → Auth Proxy → http_server.py → MCP Tools
              ↓
    (OAuth/OIDC authentication)
```

**Pros**: No code changes for auth, battle-tested
**Cons**: Additional service to deploy
**Effort**: Medium

---

## 6. Recommended Approaches by Use Case

### Use Case 1: Personal Remote Access
**Goal**: Access your MCP tools from anywhere

**Recommended Stack**:
- **Deployment**: Railway or self-hosted VPS
- **Auth**: API Keys (simple, sufficient for single user)
- **Architecture**: Direct HTTP + API key middleware

**Implementation**:
1. Add API key check to `http_server.py` (~20 lines)
2. Deploy to Railway
3. Store API key securely

### Use Case 2: ChatGPT Integration
**Goal**: Use MCP tools from ChatGPT Actions

**Recommended Stack**:
- **Deployment**: Railway (already configured) or Cloud Run
- **Auth**: API Keys (ChatGPT supports custom headers)
- **Architecture**: Direct HTTP with OpenAPI spec

**Implementation**:
1. Add API key middleware
2. Ensure `/openapi.json` endpoint works
3. Configure ChatGPT Action with your URL + API key

### Use Case 3: Team/Multi-User Access
**Goal**: Multiple people access with their own credentials

**Recommended Stack**:
- **Deployment**: Cloud Run or AWS
- **Auth**: OAuth 2.0 (Auth0 free tier)
- **Architecture**: Auth proxy or OAuth middleware

**Implementation**:
1. Set up Auth0 application
2. Add JWT validation middleware
3. Deploy with proper secrets management

### Use Case 4: Public API
**Goal**: Let anyone use your MCP tools

**Recommended Stack**:
- **Deployment**: AWS API Gateway + Lambda
- **Auth**: OAuth 2.0 with API key fallback
- **Architecture**: Full API Gateway pattern

**Implementation**:
1. Package for Lambda
2. Set up API Gateway with usage plans
3. Implement OAuth and API key auth
4. Add rate limiting and quotas

### Use Case 5: CI/CD Pipeline Access
**Goal**: Automated tools access from build systems

**Recommended Stack**:
- **Deployment**: Any (Railway, Cloud Run, self-hosted)
- **Auth**: API Keys with IP allowlisting
- **Architecture**: Direct HTTP + firewall rules

**Implementation**:
1. Add API key middleware
2. Configure IP allowlist for CI/CD runners
3. Store key in CI/CD secrets

---

## 7. Implementation Roadmap

### Phase 1: Secure Existing Server (1-2 hours)
- [ ] Add API key authentication to `http_server.py`
- [ ] Restrict CORS to specific origins
- [ ] Add rate limiting (Flask-Limiter)
- [ ] Add security audit logging

### Phase 2: Deploy to Cloud (1-2 hours)
- [ ] Choose platform (Railway recommended for quick start)
- [ ] Configure environment variables
- [ ] Deploy and verify HTTPS works
- [ ] Test all endpoints

### Phase 3: Production Hardening (2-4 hours)
- [ ] Add proper error handling
- [ ] Implement request timeouts
- [ ] Add health check monitoring
- [ ] Document API for users

### Phase 4: Advanced Security (Optional, 4-8 hours)
- [ ] Implement OAuth 2.0 (if multi-user)
- [ ] Add WAF rules
- [ ] Set up alerting for suspicious activity
- [ ] Regular security audits

---

## 8. Quick Start: Minimum Viable Security

If you want to get started quickly with basic security:

**Files to modify**: `docs-mcp/http_server.py`

**Changes needed**:
1. Add API key check before request processing
2. Add rate limiting
3. Restrict CORS
4. Deploy to Railway

**Estimated effort**: 1-2 hours

---

## Appendix: Resources

### Official Documentation
- [MCP Transports Specification](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports)
- [MCP Security Best Practices](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices)

### Security Research
- [Palo Alto: MCP Security Exposed](https://live.paloaltonetworks.com/t5/community-blogs/mcp-security-exposed-what-you-need-to-know-now/ba-p/1227143)
- [Microsoft: MCP Security Risks](https://techcommunity.microsoft.com/blog/microsoft-security-blog/understanding-and-mitigating-security-risks-in-mcp-implementations/4404667)
- [Google Cloud: Secure Remote MCP](https://cloud.google.com/blog/products/identity-security/how-to-secure-your-remote-mcp-server-on-google-cloud)

### Tools & Libraries
- [mcp-proxy](https://github.com/sparfenyuk/mcp-proxy) - stdio to HTTP proxy
- [supergateway](https://github.com/supercorp-ai/supergateway) - Bidirectional transport converter
- [Flask-Limiter](https://flask-limiter.readthedocs.io/) - Rate limiting
- [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/) - JWT auth

---

## Decision: Next Steps?

Based on this research, what would you like to do?

1. **Quick Start**: Add API key auth to existing `http_server.py` and deploy to Railway
2. **Full Security**: Implement OAuth 2.0 with proper auth proxy
3. **Research More**: Deep dive into specific platform or auth method
4. **Custom**: Different approach based on your specific needs

# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it by emailing:
**tanveer.ahmed986@example.com**

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will respond within 48 hours and work on a fix as soon as possible.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Security Best Practices

When deploying this system:
1. **Never commit `.env` files** with real credentials
2. **Use strong API keys** (minimum 32 characters, random)
3. **Enable HTTPS** in production
4. **Restrict database access** to backend only
5. **Regularly update dependencies** (`pip install -U`, `npm audit fix`)
6. **Monitor audit logs** for suspicious activity
7. **Use environment-specific configs** (dev vs prod)

## Known Security Considerations

### API Authentication
- The `/retrain` endpoint requires API key authentication via `X-API-Key` header
- Default API key in `.env.example` is `change-me-in-production` - **MUST** be changed

### Rate Limiting
- Default: 100 requests/second per IP
- Configure via `RATE_LIMIT_PER_SECOND` environment variable

### Data Privacy
- No PII (Personally Identifiable Information) is logged
- Credit card numbers and CVV are **never** stored
- User IDs and IPs are one-way hashed before storage
- GDPR and PCI-DSS compliant architecture

### Database Security
- Use strong passwords for PostgreSQL
- Restrict database access to backend service only
- Enable SSL connections in production
- Regular backups with encryption

### Docker Security
- Images run as non-root users
- No sensitive data in Docker images
- Use secrets management for production deployments

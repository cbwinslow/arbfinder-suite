# Security Policy

## Supported Versions

We release security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.4.x   | :white_check_mark: |
| 0.3.x   | :white_check_mark: |
| < 0.3   | :x:                |

## Reporting a Vulnerability

The ArbFinder Suite team takes security bugs seriously. We appreciate your efforts to responsibly disclose your findings.

### How to Report a Security Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via one of the following methods:

1. **GitHub Security Advisories** (Preferred)
   - Go to https://github.com/cbwinslow/arbfinder-suite/security/advisories
   - Click "Report a vulnerability"
   - Fill in the details of the vulnerability

2. **Email**
   - Send details to the repository maintainer
   - Include "SECURITY" in the subject line
   - Provide as much detail as possible

### What to Include

Please include the following information in your report:

- Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours
- **Communication**: We will keep you informed about the progress of fixing the vulnerability
- **Timeline**: We aim to address critical vulnerabilities within 7 days
- **Credit**: With your permission, we will credit you for discovering the vulnerability

## Security Best Practices

### For Users

When using ArbFinder Suite:

1. **Keep Updated**: Always use the latest version
2. **API Keys**: Never commit API keys or secrets to version control
3. **Environment Variables**: Use `.env` files for sensitive configuration (never commit these)
4. **Database Security**: Keep database files secure with proper permissions
5. **HTTPS**: Use HTTPS for production deployments
6. **Rate Limiting**: Implement rate limiting to prevent abuse

### For Developers

When contributing to ArbFinder Suite:

1. **Dependencies**: Keep dependencies updated (use Renovate bot)
2. **Input Validation**: Always validate and sanitize user input
3. **Authentication**: Implement proper authentication for protected endpoints
4. **SQL Injection**: Use parameterized queries (SQLite library handles this)
5. **XSS Protection**: Sanitize output in the frontend
6. **CORS**: Configure CORS properly for production
7. **Secrets Management**: Never hardcode secrets in source code
8. **Code Review**: All security-sensitive changes must be reviewed

## Known Security Considerations

### Current Security Features

- ✅ Input validation on API endpoints
- ✅ Parameterized SQL queries to prevent SQL injection
- ✅ Rate limiting built into web scrapers
- ✅ CORS configuration for API
- ✅ Environment variable support for secrets
- ✅ HTTPS support in production deployments

### Planned Security Enhancements

- [ ] API authentication and authorization
- [ ] OAuth integration for multi-user support
- [ ] Enhanced rate limiting on API endpoints
- [ ] Audit logging for security events
- [ ] Security headers (CSP, HSTS, etc.)
- [ ] Automated security scanning in CI/CD

## Security Tools

We use the following tools to maintain security:

- **CodeQL**: Automated code security scanning
- **Dependabot/Renovate**: Automated dependency updates
- **Pre-commit Hooks**: Code quality checks before commit
- **Penetration Testing**: Regular security assessments

## Vulnerability Disclosure Policy

- We practice responsible disclosure
- We will coordinate with you on disclosure timing
- We request that you do not publicly disclose the vulnerability until we have addressed it
- We will credit researchers who report valid vulnerabilities (unless they prefer to remain anonymous)

## Security Updates

Security updates will be:

1. Released as soon as possible after a fix is developed
2. Documented in the CHANGELOG with a [SECURITY] prefix
3. Announced in GitHub Security Advisories
4. Tagged with a security label in releases

## Questions?

If you have questions about this security policy, please open a discussion on GitHub or contact the maintainers.

## Attribution

Thank you to all security researchers who have responsibly disclosed vulnerabilities to us.

---

**Last Updated**: December 2024

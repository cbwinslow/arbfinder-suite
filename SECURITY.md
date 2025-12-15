# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.4.x   | :white_check_mark: |
| 0.3.x   | :white_check_mark: |
| < 0.3   | :x:                |

## Reporting a Vulnerability

We take the security of ArbFinder Suite seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Where to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via one of the following methods:

1. **Email**: Send details to the repository maintainer
2. **GitHub Security Advisories**: Use the [Security Advisory](https://github.com/cbwinslow/arbfinder-suite/security/advisories/new) feature
3. **Private Vulnerability Reporting**: Use GitHub's private vulnerability reporting feature

### What to Include

Please include the following information in your report:

- Type of vulnerability (e.g., SQL injection, XSS, authentication bypass)
- Full paths of source file(s) related to the vulnerability
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the vulnerability, including how an attacker might exploit it

### Response Timeline

- We will acknowledge receipt of your vulnerability report within 48 hours
- We will provide a detailed response within 7 days indicating next steps
- We will keep you informed of the progress towards fixing the vulnerability
- We may ask for additional information or guidance

### Disclosure Policy

- We follow the principle of [Coordinated Vulnerability Disclosure](https://vuls.cert.org/confluence/display/CVD/Executive+Summary)
- We request that you do not publicly disclose the vulnerability until we have released a fix
- Once a fix is released, we will credit you (unless you prefer to remain anonymous) in:
  - The security advisory
  - The release notes
  - The CHANGELOG.md file

### Security Best Practices

When using ArbFinder Suite, we recommend:

#### For Users
- Always use the latest version
- Use environment variables for sensitive configuration (API keys, database credentials)
- Never commit `.env` files or configuration files with secrets to version control
- Use HTTPS for all API communications
- Implement rate limiting for API endpoints
- Use strong authentication mechanisms in production
- Regularly backup your database
- Keep all dependencies up to date

#### For Developers
- Follow secure coding practices
- Validate and sanitize all user inputs
- Use parameterized queries to prevent SQL injection
- Implement proper authentication and authorization
- Use HTTPS for all external API calls
- Never log sensitive information
- Keep dependencies updated and audit them regularly (`npm audit`, `pip-audit`)
- Use environment variables for secrets, never hardcode them
- Implement proper error handling without exposing sensitive information

### Known Security Considerations

#### API Security
- The default setup does not include authentication - implement authentication before exposing the API publicly
- Rate limiting is not enabled by default - configure rate limiting in production
- CORS is configured to allow all origins by default - restrict this in production

#### Database Security
- SQLite is used by default - consider PostgreSQL for production use
- Database files should have appropriate file permissions
- Regular backups should be encrypted

#### Scraping Ethics and Legal
- Always respect robots.txt
- Implement rate limiting to avoid overloading target servers
- Review and comply with Terms of Service of each marketplace
- Some marketplaces may prohibit automated access

### Security Tools

We use the following tools to maintain security:

- **Dependabot**: Automated dependency updates
- **CodeQL**: Static analysis for security vulnerabilities
- **pip-audit**: Python dependency vulnerability scanning
- **npm audit**: JavaScript dependency vulnerability scanning

### Security Updates

Security updates will be released as soon as possible and will be clearly marked in:
- GitHub Security Advisories
- Release notes with `[SECURITY]` prefix
- CHANGELOG.md with security section

### Bug Bounty Program

We currently do not have a bug bounty program. However, we deeply appreciate security researchers who responsibly disclose vulnerabilities and will publicly acknowledge their contributions.

### Attribution

We would like to thank the following security researchers for their responsible disclosure:

<!-- This section will be updated as researchers contribute -->

- Your name could be here!

### Questions

If you have questions about this security policy, please open a GitHub Discussion or contact the maintainers.

---

**Last Updated**: 2025-12-15

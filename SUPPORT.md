# Support

Thank you for using ArbFinder Suite! This document provides information on how to get help and support.

## 📚 Documentation

Before asking for help, please check our documentation:

### Getting Started
- [README.md](README.md) - Main documentation and quick start guide
- [Quick Start Guide](docs/getting-started/QUICKSTART.md) - Quick setup instructions
- [Developer Guide](docs/development/DEVELOPER.md) - Developer setup and guidelines
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute to the project

### Component Documentation
- [TUI Documentation](docs/tui/README.md) - Go TUI interface guide
- [TUI Architecture](docs/tui/ARCHITECTURE.md) - TUI design and structure
- [API Documentation](README.md#api-endpoints) - API endpoints and usage
- [TypeScript SDK](packages/client/README.md) - Node.js/TypeScript client library

### Guides and Tutorials
- [Examples](docs/guides/EXAMPLES.md) - Usage examples
- [CI/CD Guide](docs/development/CI_CD_AUTOMATION.md) - Automation setup
- [Platform Guide](docs/platform/PLATFORM_GUIDE.md) - Platform deployment
- [Enterprise Roadmap](docs/development/ENTERPRISE_ROADMAP.md) - Enterprise features

## 🐛 Found a Bug?

If you've found a bug, please:

1. **Search existing issues** to see if it's already reported
2. **Check the documentation** to ensure it's not expected behavior
3. **Create a bug report** using our [bug report template](https://github.com/cbwinslow/arbfinder-suite/issues/new?template=bug_report.yml)

Include:
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python/Node version)
- Error messages or logs

## 💡 Have a Feature Request?

We love hearing ideas! Please:

1. **Search existing issues** to see if it's already suggested
2. **Check the roadmap** in [README.md](README.md#roadmap) to see if it's planned
3. **Create a feature request** using our [feature request template](https://github.com/cbwinslow/arbfinder-suite/issues/new?template=feature_request.yml)

Include:
- The problem you're trying to solve
- Your proposed solution
- Use cases and examples
- Any alternatives you've considered

## ❓ Have a Question?

### Quick Questions

For quick questions, check:
- [FAQ Section](#frequently-asked-questions) below
- [Existing GitHub Issues](https://github.com/cbwinslow/arbfinder-suite/issues)
- [GitHub Discussions](https://github.com/cbwinslow/arbfinder-suite/discussions)

### Detailed Questions

For more detailed questions or discussions:

1. **Use GitHub Discussions** - [Start a discussion](https://github.com/cbwinslow/arbfinder-suite/discussions/new)
   - Ask questions
   - Share ideas
   - Show what you've built
   - Help others

2. **Check Community Forums** - Coming soon!

## 🤝 Getting Help

### Self-Service Resources

1. **Read the docs** - Most questions are answered in our documentation
2. **Check examples** - See working examples in [docs/guides/EXAMPLES.md](docs/guides/EXAMPLES.md)
3. **Search issues** - Someone may have had the same problem
4. **Use the CLI help** - Run `arbfinder --help` for CLI documentation

### Community Support

- **GitHub Discussions**: Best for questions and discussions
- **GitHub Issues**: For bugs and feature requests only
- **Pull Requests**: Contributions and fixes

### Response Times

This is an open-source project maintained by volunteers:

- **Critical bugs**: 1-3 days
- **Other bugs**: 1-2 weeks
- **Feature requests**: Depends on complexity and priority
- **Questions**: 1-7 days

## 🔧 Troubleshooting

### Common Issues

#### Installation Problems

**Problem**: `pip install` fails
```bash
# Solution: Upgrade pip and setuptools
pip install --upgrade pip setuptools
pip install -e .
```

**Problem**: `npm install` fails in frontend
```bash
# Solution: Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

#### Runtime Issues

**Problem**: Database locked error
```bash
# Solution: Close other connections or wait
# SQLite only allows one writer at a time
```

**Problem**: API connection refused
```bash
# Solution: Ensure backend is running
uvicorn backend.api.main:app --reload --port 8080
```

**Problem**: CORS errors in frontend
```bash
# Solution: Set FRONTEND_ORIGIN environment variable
export FRONTEND_ORIGIN=http://localhost:3000
```

#### Provider Issues

**Problem**: No results from providers
- Check your internet connection
- Verify the provider website is accessible
- Check if the provider structure has changed
- Enable verbose logging with `-v` flag

**Problem**: Rate limiting errors
- Reduce the number of concurrent requests
- Increase delays between requests
- Use watch mode with longer intervals

### Debug Mode

Enable verbose logging to diagnose issues:

```bash
# Python CLI
arbfinder search "query" -v

# Python script
python backend/arb_finder.py "query" --verbose

# Check API logs
uvicorn backend.api.main:app --reload --log-level debug
```

### System Requirements

Minimum requirements:
- **Python**: 3.9 or higher
- **Node.js**: 16.x or higher (for frontend/packages)
- **Go**: 1.19 or higher (for TUI)
- **RAM**: 2GB minimum, 4GB recommended
- **Disk**: 500MB for application, additional for database

## 📖 Frequently Asked Questions

### General

**Q: Is ArbFinder Suite free?**
A: Yes! It's open source under the MIT license. You can use, modify, and distribute it freely.

**Q: Can I use this for commercial purposes?**
A: Yes, the MIT license allows commercial use. However, please respect the terms of service of the marketplaces you scrape.

**Q: Which marketplaces are supported?**
A: Currently: ShopGoodwill, GovDeals, GovernmentSurplus, eBay (sold comps), and Facebook Marketplace (manual import). See [README.md](README.md) for details.

### Technical

**Q: How do I add a new marketplace provider?**
A: See [CONTRIBUTING.md](CONTRIBUTING.md#new-providers) for detailed instructions on adding providers.

**Q: Can I run this on a schedule?**
A: Yes! Use watch mode (`--watch`) or set up a cron job. See [documentation](README.md#watch-mode) for details.

**Q: How do I export data?**
A: Use `--csv` or `--json` flags with the CLI, or call the API endpoints to get data programmatically.

**Q: Is there a rate limit?**
A: The application has built-in rate limiting to be respectful to source websites. You can adjust this in the configuration.

### Deployment

**Q: Can I deploy this to production?**
A: Yes! See [docs/platform/PLATFORM_GUIDE.md](docs/platform/PLATFORM_GUIDE.md) for deployment instructions. Consider security best practices in [SECURITY.md](SECURITY.md).

**Q: Does it support Docker?**
A: Yes! Use `docker-compose up` to run all services. See [README.md](README.md#using-docker) for details.

**Q: How do I scale this application?**
A: You can run multiple instances of the crawler with different queries, or use a task queue like Celery. See [docs/development/ENTERPRISE_ROADMAP.md](docs/development/ENTERPRISE_ROADMAP.md).

### Data and Privacy

**Q: What data is stored?**
A: Only publicly available listings data (title, price, URL, etc.). No personal information is collected from users.

**Q: Can I delete data?**
A: Yes, use database utilities: `arbfinder db clean --days 30` or manually delete records from the SQLite database.

**Q: Is my data secure?**
A: Data is stored locally in a SQLite database. For production deployments, follow security best practices in [SECURITY.md](SECURITY.md).

## 🚀 Feature Requests and Roadmap

Check our [roadmap](README.md#roadmap) to see what's planned. Want to suggest something new? [Open a feature request](https://github.com/cbwinslow/arbfinder-suite/issues/new?template=feature_request.yml)!

## 🤝 Contributing

Want to help improve ArbFinder Suite? We'd love your contribution!

- See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines
- Check [good first issues](https://github.com/cbwinslow/arbfinder-suite/labels/good%20first%20issue)
- Join discussions to help others

## 📧 Contact

- **GitHub Issues**: [Report bugs or request features](https://github.com/cbwinslow/arbfinder-suite/issues)
- **GitHub Discussions**: [Ask questions or share ideas](https://github.com/cbwinslow/arbfinder-suite/discussions)
- **Security Issues**: Use [GitHub Security Advisories](https://github.com/cbwinslow/arbfinder-suite/security/advisories/new)

## 🙏 Acknowledgments

Thank you to all our contributors and users! Your feedback and contributions make this project better.

---

**Still need help?** Don't hesitate to [open a discussion](https://github.com/cbwinslow/arbfinder-suite/discussions/new) or [create an issue](https://github.com/cbwinslow/arbfinder-suite/issues/new/choose). We're here to help!

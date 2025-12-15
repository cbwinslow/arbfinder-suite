# Support

Thank you for using ArbFinder Suite! This document provides information on how to get help.

## Getting Help

### Documentation

Before asking for help, please check our documentation:

- **[README.md](README.md)** - Overview, installation, and basic usage
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide
- **[DEVELOPER.md](DEVELOPER.md)** - Developer documentation
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contributing guidelines
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes
- **[docs/](docs/)** - Additional documentation

### Common Issues

#### Installation Issues

**Problem**: `pip install -e .` fails
- **Solution**: Ensure you have Python 3.9+ installed
- **Solution**: Try upgrading pip: `pip install --upgrade pip`
- **Solution**: Install build tools: `pip install build setuptools wheel`

**Problem**: Frontend won't start
- **Solution**: Ensure Node.js 16+ is installed
- **Solution**: Delete `node_modules` and run `npm install` again
- **Solution**: Clear npm cache: `npm cache clean --force`

#### Runtime Issues

**Problem**: Database errors
- **Solution**: Check database file permissions
- **Solution**: Try `arbfinder db vacuum` to repair the database
- **Solution**: Delete the database file to start fresh (you'll lose data)

**Problem**: API connection errors
- **Solution**: Ensure the backend server is running on port 8080
- **Solution**: Check firewall settings
- **Solution**: Verify `NEXT_PUBLIC_API_BASE` environment variable

**Problem**: Import errors
- **Solution**: Reinstall with `pip install -e ".[dev,test]"`
- **Solution**: Check that you're in the correct virtual environment
- **Solution**: Verify Python path includes the package

### Search Existing Issues

Check if someone else has already reported your issue:

1. Go to [Issues](https://github.com/cbwinslow/arbfinder-suite/issues)
2. Use the search bar to look for similar issues
3. Check both open and closed issues
4. Review the comments for potential solutions

### GitHub Discussions

For questions, ideas, and general discussion:

- **[Discussions](https://github.com/cbwinslow/arbfinder-suite/discussions)**
  - **Q&A**: Ask questions and get answers
  - **Ideas**: Share feature ideas
  - **Show and Tell**: Share what you built
  - **General**: General discussion

### Create an Issue

If you can't find a solution, create an issue:

1. Go to [Issues](https://github.com/cbwinslow/arbfinder-suite/issues/new/choose)
2. Choose the appropriate template:
   - **Bug Report**: For bugs and errors
   - **Feature Request**: For new features
   - **Documentation**: For documentation improvements
   - **Task**: For project tasks
3. Fill out the template completely
4. Provide as much detail as possible

## Support Levels

### Community Support (Free)

- GitHub Issues
- GitHub Discussions
- Community contributions
- Best-effort response time

**Response Time**: Usually within 1-7 days

### What We Support

✅ Installation and setup help
✅ Bug reports and fixes
✅ Feature requests (evaluated for inclusion)
✅ Documentation improvements
✅ General usage questions
✅ Development questions

### What We Don't Support

❌ Custom development work
❌ Integration with proprietary systems
❌ Production deployment support
❌ 24/7 support or SLA guarantees
❌ Phone support
❌ Remote debugging of your environment

## Resources

### Learning Resources

- **Python**: [Python Documentation](https://docs.python.org/)
- **FastAPI**: [FastAPI Documentation](https://fastapi.tiangolo.com/)
- **Next.js**: [Next.js Documentation](https://nextjs.org/docs)
- **TypeScript**: [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- **Docker**: [Docker Documentation](https://docs.docker.com/)

### Project Resources

- **Repository**: https://github.com/cbwinslow/arbfinder-suite
- **Issues**: https://github.com/cbwinslow/arbfinder-suite/issues
- **Discussions**: https://github.com/cbwinslow/arbfinder-suite/discussions
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **Roadmap**: [ROADMAP.md](ROADMAP.md)

## Contributing

Want to help improve ArbFinder Suite?

- Report bugs and issues
- Suggest features and improvements
- Submit pull requests
- Improve documentation
- Help others in discussions

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Contact

### Maintainers

- **Primary Maintainer**: See repository owner
- **Response Time**: Best effort, usually within 1-7 days

### How to Contact

1. **GitHub Issues**: For bugs and features
2. **GitHub Discussions**: For questions and ideas
3. **Pull Requests**: For contributions

**Please do not email maintainers directly for support.** Use GitHub Issues and Discussions so others can benefit from the answers.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

- Be respectful and constructive
- Help others when you can
- Follow the [contributing guidelines](CONTRIBUTING.md)
- Report inappropriate behavior to maintainers

## Frequently Asked Questions

### General Questions

**Q: Is ArbFinder Suite free to use?**
A: Yes, it's open source under the MIT License.

**Q: Can I use this commercially?**
A: Yes, the MIT License allows commercial use.

**Q: Do you offer paid support?**
A: Currently, only community support is available.

### Technical Questions

**Q: What Python version is required?**
A: Python 3.9 or higher.

**Q: Can I run this on Windows?**
A: Yes, it works on Windows, macOS, and Linux.

**Q: Does this work with Python 3.12?**
A: Yes, it supports Python 3.9 through 3.12+.

**Q: Can I deploy this to cloud services?**
A: Yes, see the Docker documentation for deployment options.

### Usage Questions

**Q: How do I add a new marketplace provider?**
A: See the [CONTRIBUTING.md](CONTRIBUTING.md) guide for adding providers.

**Q: Can I export data to Excel?**
A: Currently supports CSV and JSON. Excel export is planned.

**Q: Does this support international marketplaces?**
A: Currently focused on US marketplaces, but international support is planned.

## Security Issues

For security vulnerabilities, please see [SECURITY.md](SECURITY.md) for responsible disclosure guidelines.

**Do not report security issues in public issues or discussions.**

## Acknowledgments

Thank you to all contributors and users who help make ArbFinder Suite better!

---

**Last Updated**: December 2024

**Need help? Start with the [documentation](README.md) → Try [discussions](https://github.com/cbwinslow/arbfinder-suite/discussions) → Create an [issue](https://github.com/cbwinslow/arbfinder-suite/issues/new/choose)**

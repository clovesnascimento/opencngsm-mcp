# Contributing to OpenCngsm

Thank you for your interest in contributing to OpenCngsm v3.3! 🛡️

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)
- [Security Vulnerabilities](#security-vulnerabilities)
- [Pull Requests](#pull-requests)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)

---

## 📜 Code of Conduct

This project follows the **Escoteiro Hacker Code of Conduct**:

1. Use technology for good
2. Respect privacy and data
3. Never invade systems
4. Document everything meticulously
5. Share knowledge
6. Seek continuous improvement
7. Implement security at all layers
8. Test before deploying

---

## 🤝 How Can I Contribute?

### Reporting Bugs
See [Reporting Bugs](#reporting-bugs) section below.

### Suggesting Features
See [Suggesting Features](#suggesting-features) section below.

### Improving Documentation
- Fix typos or clarify instructions
- Add examples or tutorials
- Translate documentation

### Writing Code
- Fix bugs
- Implement features
- Improve performance
- Add tests

---

## 🐛 Reporting Bugs

1. **Search existing issues** to avoid duplicates
2. **Use the bug report template** when creating a new issue
3. **Provide detailed information:**
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details
   - Logs and screenshots

**Template:** [Bug Report](.github/ISSUE_TEMPLATE/bug_report.md)

---

## 💡 Suggesting Features

1. **Check existing feature requests** to avoid duplicates
2. **Use the feature request template**
3. **Explain the problem** you're trying to solve
4. **Describe your proposed solution**
5. **Consider security implications**

**Template:** [Feature Request](.github/ISSUE_TEMPLATE/feature_request.md)

---

## 🔒 Security Vulnerabilities

**DO NOT open public issues for security vulnerabilities.**

### Responsible Disclosure:
- **Email:** opencngsm@cngsm.education
- **Subject:** `[SECURITY] OpenCngsm v3.3 Vulnerability Report`
- **Response Time:** 24-48 hours

### What to Include:
- Detailed description
- Steps to reproduce
- Proof of concept (if applicable)
- Suggested fix (if you have one)

---

## 🔀 Pull Requests

### Before Submitting:

1. **Fork the repository**
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Test thoroughly**
5. **Update documentation**
6. **Commit with clear messages:**
   ```bash
   git commit -m "feat: add new security pattern for XYZ"
   ```

### PR Guidelines:

- ✅ One feature/fix per PR
- ✅ Clear description of changes
- ✅ Reference related issues
- ✅ Include tests
- ✅ Update documentation
- ✅ Follow coding standards
- ✅ Pass all CI checks

### Commit Message Format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `security`: Security improvements

**Example:**
```
feat(gsec): add Stage 14 for API rate limiting

Implements new security stage to prevent API abuse through
intelligent rate limiting based on user behavior patterns.

Closes #123
```

---

## 🛠️ Development Setup

### Prerequisites:
- Python 3.11+
- Git
- Docker (optional)

### Setup:

```bash
# Clone repository
git clone https://github.com/clovesnascimento/opencngsm-mcp.git
cd opencngsm-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run security tests
pytest tests/security/
```

---

## 📏 Coding Standards

### Python:

- **Style:** PEP 8
- **Formatter:** Black
- **Linter:** Flake8
- **Type Hints:** Use type hints for all functions
- **Docstrings:** Google style

### Example:

```python
def validate_prompt(text: str, enable_llm_judge: bool = True) -> tuple[bool, str]:
    """
    Validate user prompt against security patterns.
    
    Args:
        text: The user input to validate
        enable_llm_judge: Whether to use LLM Judge for validation
        
    Returns:
        Tuple of (is_valid, reason)
        
    Raises:
        ValueError: If text is empty
    """
    if not text:
        raise ValueError("Text cannot be empty")
    
    # Implementation
    return (True, "Validation passed")
```

### Security Code:

- **Always validate input**
- **Use parameterized queries**
- **Never log sensitive data**
- **Add comments for security-critical code**
- **Include tests for security features**

---

## ✅ Testing

### Running Tests:

```bash
# All tests
pytest

# Security tests only
pytest tests/security/

# Specific test file
pytest tests/security/test_stage13_iot_injection.py

# With coverage
pytest --cov=core --cov-report=html
```

### Writing Tests:

- Test all security patterns
- Test edge cases
- Test error handling
- Aim for 80%+ coverage

---

## 📚 Documentation

### Update Documentation When:

- Adding new features
- Changing APIs
- Fixing bugs that affect usage
- Adding security patterns

### Documentation Locations:

- `README.md` - Main documentation
- `docs/` - Detailed guides
- Code comments - Implementation details
- Docstrings - Function/class documentation

---

## 🎓 Learning Resources

- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [MITRE ATLAS](https://atlas.mitre.org/)
- [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework)
- [Security Certificate](docs/security_certificate.md)

---

## 💬 Questions?

- **Discussions:** https://github.com/clovesnascimento/opencngsm-mcp/discussions
- **Email:** opencngsm@cngsm.education
- **Issues:** https://github.com/clovesnascimento/opencngsm-mcp/issues

---

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in security advisories (if applicable)

---

**Thank you for contributing to OpenCngsm! 🛡️**

**Classification:** PRODUCTION-GRADE SECURITY++ (MILITARY-GRADE)

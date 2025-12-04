# Changelog - AutoCommit CLI

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [2.1.0] - 2025-12-03 - Security Hardened Edition 🛡️

### 🚨 CRITICAL SECURITY FIXES
- **FIXED**: Shell injection vulnerability in `subprocess.run()` calls
- **FIXED**: Input validation bypass allowing malicious commands
- **FIXED**: Log file growth without rotation limits
- **FIXED**: Easily evadable sensitive file scanner

### ✨ Added - New Security Features
- Complete input validation with `validate_git_input()` function
- Robust sensitive file scanner with regex patterns and content analysis  
- Secure command execution with `run_command_secure()` (shell=False)
- Automatic log rotation when files exceed 10MB
- Security timeouts (30s) for all Git operations
- Enhanced confirmation system requiring exact "CONFIRMO" input
- Sanitization of sensitive data in logs (passwords, tokens, keys)
- Comprehensive security test suite with pytest
- CI/CD pipeline with GitHub Actions
- Security analysis with Bandit and Safety tools

### 🔧 Changed - Security Improvements
- Refactored all `subprocess.run()` calls to use argument lists instead of shell commands
- Enhanced logging with version info, OS detection, and error context
- Improved error handling with specialized `SecurityError` exception
- Better user feedback with step-by-step progress indicators
- Stricter filename validation for Git operations
- Case-insensitive sensitive file detection

### 📚 Documentation
- Updated README with v2.1 security features and installation guides
- Added comprehensive testing instructions and developer guidelines
- Security best practices documentation
- Troubleshooting guide updated with new error scenarios
- Code of conduct and contribution guidelines

### 🧪 Testing & Quality Assurance
- 15+ security-focused unit tests covering injection attacks
- Input validation boundary testing
- Mock-based testing for subprocess operations
- GitHub Actions CI/CD with automated security scanning
- Code quality tools: Black, Flake8, MyPy integration
- Pre-commit hooks configuration

### 📦 Dependencies
- Added development dependencies for testing and code quality
- Security analysis tools (bandit, safety)
- Code formatting and linting tools (black, flake8, mypy)

### 🏗️ Infrastructure  
- GitHub Actions workflow for continuous security validation
- Automated testing on Windows, security scanning on Linux
- Coverage reporting and artifact collection
- Release readiness validation pipeline

---

## [2.0.0] - 2025-12-02 - Enhanced Features

### Added
- Basic logging system with persistent log files
- Simple sensitive file detection for common patterns (.env, .key, etc.)
- Multi-account SSH configuration documentation
- Improved user interface with emojis and progress indicators
- Project selection menu when outside Git repositories

### Changed
- Enhanced error messages with contextual diagnostics
- Better handling of Git conflicts and SSH permission errors
- Improved documentation with step-by-step installation guides

---

## [1.0.0] - 2025-11-XX - Initial Release

### Added
- Basic Git workflow automation (add, commit, push)
- Windows-focused design with accessibility considerations
- Simple project detection and selection
- Basic error handling and user feedback
- MIT License
- Initial README documentation

### Known Issues (Resolved in v2.1)
- Shell injection vulnerabilities in command execution
- Insufficient input validation
- Basic sensitive file detection easily bypassed
- No automated testing or security validation

---

## Security Advisories

### CVE-2025-AUTOCOMMIT-01 (Fixed in v2.1.0)
**Severity**: Critical  
**Description**: Shell injection vulnerability allowing arbitrary command execution  
**Affected Versions**: All versions < 2.1.0  
**Fix**: Upgrade to v2.1.0 immediately  

### CVE-2025-AUTOCOMMIT-02 (Fixed in v2.1.0)  
**Severity**: High  
**Description**: Input validation bypass allowing malicious filename/branch/message injection  
**Affected Versions**: All versions < 2.1.0  
**Fix**: Upgrade to v2.1.0 immediately

---

## Migration Guide: v2.0 → v2.1

### Immediate Action Required
If you're using any version prior to v2.1.0:

1. **Stop using the tool immediately** in production environments
2. **Backup your important repositories** before upgrading
3. **Download v2.1.0** from the official GitHub repository
4. **Replace old files** with the new secure version
5. **Run security tests**: `pytest tests/test_security.py`
6. **Verify upgrade**: Check logs for "v2.1 Security Hardened" message

### Breaking Changes
- None - v2.1 maintains full backward compatibility
- Log format enhanced with additional security information
- Stricter input validation may reject previously accepted malicious inputs (this is intended)

### New Requirements
- No new external dependencies for core functionality
- Development dependencies added for testing and security analysis
- Python 3.7+ still supported

---

## Roadmap

### v2.2 (January 2026) - Cross-Platform Support
- Linux and macOS compatibility
- Enhanced Git flow integration
- Conventional commits support
- Performance optimizations

### v2.3 (Q1 2026) - Advanced Features  
- Web dashboard for repository metrics
- Integration with GitHub/GitLab APIs
- Advanced conflict resolution helpers
- Team collaboration features

### v3.0 (Q2 2026) - Enterprise Edition
- Plugin system architecture
- RBAC (Role-Based Access Control)
- Enterprise compliance reporting
- SSO integration capabilities

---

*For detailed technical information about security improvements, see the updated `analisis.md` file.*
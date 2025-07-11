# Security Policy

## 🔒 Security Considerations

The Universal Markdown Audio Transcription System is designed with privacy and security as core principles. This document outlines our security practices and how to report security issues.

## 🛡️ Privacy by Design

### Local Processing
- **No Cloud Dependencies**: All transcription happens locally on your machine
- **No API Keys Required**: No external services or accounts needed
- **No Data Transmission**: Audio files never leave your device
- **No Telemetry**: No usage data is collected or transmitted

### Data Handling
- **File Permissions**: Respects system file permissions
- **Temporary Files**: Secure cleanup of temporary processing files
- **Log Security**: Logs contain no sensitive audio content
- **Configuration Safety**: Configuration files are stored locally

## 🔐 Security Features

### File System Security
- **Path Validation**: All file paths are validated and sanitized
- **Directory Traversal Protection**: Prevents access outside configured directories
- **Permission Checks**: Verifies read/write permissions before processing
- **Lock Files**: Prevents multiple instances from conflicting

### Process Security
- **Sandboxed Execution**: Whisper runs in controlled environment
- **Resource Limits**: Prevents resource exhaustion attacks
- **Error Handling**: Secure error messages that don't leak system information
- **Input Validation**: All configuration inputs are validated

### System Integration
- **User Isolation**: Runs under user context, not system
- **No Root Required**: Normal user permissions sufficient
- **Systemd Security**: Service files include security restrictions
- **Log Rotation**: Prevents log files from growing unbounded

## 🚨 Threat Model

### Threats We Protect Against
1. **Data Exfiltration**: Audio content being sent to external services
2. **Path Traversal**: Malicious file paths accessing unauthorized areas
3. **Resource Exhaustion**: Large files consuming excessive system resources
4. **Configuration Injection**: Malicious configuration values
5. **Privilege Escalation**: Unauthorized system access

### Out of Scope
- **Physical Security**: Physical access to the machine
- **OS-level Vulnerabilities**: Operating system security is user's responsibility
- **Network Security**: Network configuration and firewall rules
- **Malware Protection**: Antivirus and anti-malware solutions

## 🔍 Security Best Practices

### For Users

#### Installation Security
```bash
# Verify checksums when downloading
sha256sum markdown-audio-transcription.tar.gz

# Use virtual environments
python -m venv .venv
source .venv/bin/activate

# Keep dependencies updated
pip install --upgrade -r requirements.txt
```

#### Configuration Security
```yaml
# Use absolute paths
vault_path: "/home/user/Documents/Notes"

# Secure log locations
log_file: "/home/user/.local/share/markdown-transcription/app.log"

# Don't use system directories
temp_dir: "/tmp/markdown-transcription"
```

#### File System Security
```bash
# Set appropriate file permissions
chmod 600 config.yaml
chmod 700 ~/.config/markdown-transcription/

# Regular security updates
sudo apt update && sudo apt upgrade
```

### For Administrators

#### System Service Security
```ini
# Systemd service security settings
[Service]
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=false
ReadWritePaths=/home/user/Notes
```

#### Network Security
```bash
# No network access required, but if using network storage:
# Ensure secure mounting of network drives
# Use encrypted connections (SFTP, etc.)
```

#### Monitoring
```bash
# Monitor log files for suspicious activity
sudo journalctl -u markdown-transcription.service -f

# Regular security audits
sudo find /home/user/Notes -type f -name "*.md" -exec grep -l "suspicious_pattern" {} \;
```

## 🚫 Common Security Mistakes

### ❌ Don't Do This
```yaml
# DON'T: Use root directories
vault_path: "/root/notes"

# DON'T: Use system temp directories without subdirectories
temp_dir: "/tmp"

# DON'T: Store logs in world-writable locations
log_file: "/tmp/app.log"

# DON'T: Use overly permissive file permissions
# chmod 777 config.yaml  # NEVER DO THIS
```

### ✅ Do This Instead
```yaml
# DO: Use user home directories
vault_path: "/home/user/Documents/Notes"

# DO: Use application-specific temp directories
temp_dir: "/tmp/markdown-transcription"

# DO: Store logs in user-specific locations
log_file: "/home/user/.local/share/markdown-transcription/app.log"

# DO: Use restrictive file permissions
# chmod 600 config.yaml
```

## 🛠️ Security Configuration

### Recommended Security Settings

```yaml
# Security-focused configuration
vault_path: "/home/user/Documents/Notes"
temp_dir: "/tmp/markdown-transcription"
log_file: "/home/user/.local/share/markdown-transcription/app.log"

# Restrict processing to known safe extensions
audio_extensions: [".mp3", ".wav", ".m4a", ".flac"]
video_extensions: [".mp4", ".mkv", ".avi", ".mov"]

# Enable detailed logging for security auditing
log_level: "INFO"
file_logging: true
console_logging: false

# Prevent unauthorized file access
owner_user: "your_username"
owner_group: "your_group"
```

### Security Validation Script

```bash
#!/bin/bash
# security-check.sh - Basic security validation

echo "Security Check for Markdown Transcription System"
echo "================================================"

# Check file permissions
echo "Checking file permissions..."
if [ -f "config.yaml" ]; then
    PERMS=$(stat -c "%a" config.yaml)
    if [ "$PERMS" -gt 600 ]; then
        echo "⚠️  WARNING: config.yaml has overly permissive permissions ($PERMS)"
        echo "   Run: chmod 600 config.yaml"
    else
        echo "✅ config.yaml permissions are secure"
    fi
fi

# Check for sensitive data in logs
echo "Checking for sensitive data in logs..."
if [ -f "$HOME/.local/share/markdown-transcription/app.log" ]; then
    if grep -q "password\|secret\|key" "$HOME/.local/share/markdown-transcription/app.log"; then
        echo "⚠️  WARNING: Potential sensitive data found in logs"
    else
        echo "✅ No sensitive data found in logs"
    fi
fi

# Check temp directory
echo "Checking temp directory..."
if [ -d "/tmp/markdown-transcription" ]; then
    OWNER=$(stat -c "%U" /tmp/markdown-transcription)
    if [ "$OWNER" != "$USER" ]; then
        echo "⚠️  WARNING: Temp directory owned by $OWNER, not $USER"
    else
        echo "✅ Temp directory ownership is correct"
    fi
fi

echo "Security check complete!"
```

## 🚨 Reporting Security Vulnerabilities

### How to Report

If you discover a security vulnerability, please:

1. **DO NOT** create a public issue
2. **DO NOT** discuss on public forums
3. **DO** report privately to maintainers

### Contact Information

- **Email**: security@example.com (replace with actual email)
- **GPG Key**: Available at keybase.io/username
- **Response Time**: Within 48 hours

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact assessment
- Suggested fixes (if any)
- Your contact information

### Response Process

1. **Acknowledgment**: Within 48 hours
2. **Investigation**: 1-2 weeks
3. **Fix Development**: 2-4 weeks
4. **Testing**: 1 week
5. **Release**: Coordinated disclosure
6. **Public Disclosure**: After fix is available

## 🏆 Security Credits

We recognize security researchers who help improve the project:

- [Your Name] - Responsible disclosure of [issue type]
- [Researcher Name] - Configuration security improvements

## 📋 Security Changelog

### Version 1.0.0
- Initial security implementation
- Local processing guarantee
- File system security controls
- Configuration validation

### Future Improvements
- [ ] Code signing for releases
- [ ] Automated security scanning
- [ ] Security documentation audit
- [ ] Penetration testing

## 📚 Additional Resources

### Security Tools
- [Bandit](https://bandit.readthedocs.io/) - Python security linter
- [Safety](https://pyup.io/safety/) - Dependency vulnerability scanner
- [Semgrep](https://semgrep.dev/) - Static analysis security scanner

### Security References
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python-security.readthedocs.io/)
- [Secure Coding Guidelines](https://wiki.sei.cmu.edu/confluence/display/seccode)

### Privacy Resources
- [Privacy by Design](https://www.ipc.on.ca/wp-content/uploads/resources/7foundationalprinciples.pdf)
- [GDPR Compliance](https://gdpr.eu/)
- [Data Minimization](https://edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-42020-use-location-data-and-contact-tracing_en)

## 🔐 Conclusion

Security is a shared responsibility. While we work hard to make the system secure by design, users must also follow security best practices. If you have questions about security, please don't hesitate to reach out.

**Remember**: The best security feature is that your audio never leaves your machine!
# Contributing to Universal Markdown Audio Transcription System

Thank you for your interest in contributing to the Universal Markdown Audio Transcription System! This document provides guidelines for contributing to the project.

## 🤝 How to Contribute

### Reporting Issues

Before creating an issue, please:
1. Check if the issue already exists
2. Use the issue template if available
3. Provide as much detail as possible:
   - Operating system and version
   - Python version
   - Steps to reproduce the issue
   - Expected vs actual behavior
   - Error messages and logs

### Suggesting Features

Feature requests are welcome! Please:
1. Check existing feature requests first
2. Describe the use case and benefits
3. Consider backward compatibility
4. Provide examples if applicable

### Code Contributions

#### Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/markdown-audio-transcription.git
   cd markdown-audio-transcription
   ```

3. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   ```

5. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### Development Guidelines

**Code Style:**
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all public functions and classes
- Keep functions focused and small
- Use type hints where appropriate

**Testing:**
- Write tests for new features
- Ensure existing tests pass
- Test on multiple platforms if possible
- Include edge cases in your tests

**Documentation:**
- Update README.md if needed
- Add docstrings to new functions
- Update configuration examples
- Document any new dependencies

#### Code Review Process

1. Ensure your code follows the style guidelines
2. Run tests locally before submitting
3. Create a pull request with:
   - Clear description of changes
   - Reference to related issues
   - Testing information
   - Screenshots if applicable

4. Respond to feedback promptly
5. Make requested changes
6. Rebase if necessary

### Testing

#### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_transcription_system.py

# Run tests with verbose output
pytest -v
```

#### Test Structure

```
tests/
├── test_config.py
├── test_transcription_system.py
├── test_templates.py
├── fixtures/
│   ├── sample_audio.wav
│   └── sample_config.yaml
└── conftest.py
```

## 📋 Development Setup

### Prerequisites

- Python 3.14+
- FFmpeg
- Git

### Additional Development Tools

```bash
# Install development dependencies
pip install black flake8 pytest pytest-cov mypy

# Code formatting
black src/

# Linting
flake8 src/

# Type checking
mypy src/
```

## 🔧 Project Structure

```
markdown-audio-transcription/
├── src/                          # Source code
│   ├── transcription_system.py  # Main application
│   └── config.py                # Configuration handling
├── templates/                    # Template files
├── examples/                     # Example configurations
├── scripts/                      # Helper scripts
├── docs/                         # Documentation
├── tests/                        # Test files
├── requirements.txt              # Dependencies
├── .gitignore                   # Git ignore rules
├── LICENSE                      # License file
└── README.md                    # Main documentation
```

## 📝 Commit Guidelines

### Commit Message Format

```
type(scope): description

Optional longer description

Fixes #issue_number
```

### Types

- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(config): add support for custom templates

Add ability to specify custom template paths in configuration.
This allows users to completely customize the output format.

Fixes #123
```

```
fix(transcription): handle empty audio files gracefully

Previously, empty audio files would cause the system to crash.
Now they are skipped with a warning message.

Fixes #456
```

## 🐛 Debugging

### Common Issues

1. **Whisper Installation Problems**
   ```bash
   # Recommended: Package manager installation (Ubuntu/Debian)
   sudo apt install python-openai-whisper

   # Alternative: Global pip installation
   pip install --global openai-whisper --upgrade
   ```

2. **FFmpeg Not Found**
   ```bash
   # Ubuntu/Debian
   sudo apt install ffmpeg
   
   # macOS
   brew install ffmpeg
   ```

3. **Permission Errors**
   ```bash
   # Fix file permissions
   chmod +x scripts/*.sh
   ```

### Debug Mode

Enable debug logging in configuration:
```yaml
log_level: "DEBUG"
console_logging: true
```

## 📖 Documentation

### API Documentation

- Use Google-style docstrings
- Include parameter types and return values
- Provide examples where helpful

```python
def transcribe_file(self, file_path: Path) -> bool:
    """Transcribe a single media file using Whisper.
    
    Args:
        file_path: Path to the audio/video file to transcribe
        
    Returns:
        True if transcription was successful, False otherwise
        
    Raises:
        ConfigurationError: If Whisper is not properly configured
        
    Example:
        >>> system = MarkdownTranscriptionSystem(config)
        >>> success = system.transcribe_file(Path("audio.mp3"))
    """
```

### Configuration Documentation

Document all configuration options:
```yaml
# Option description
option_name: default_value  # Valid values: option1, option2
```

## 🌐 Internationalization

### Language Support

- Template files should support multiple languages
- Error messages should be clear and helpful
- Consider character encoding issues

### Adding New Languages

1. Create language-specific templates
2. Update configuration options
3. Test with non-ASCII characters
4. Document language-specific features

## 🔐 Security

### Guidelines

- Never commit sensitive data
- Validate all user inputs
- Use secure file handling
- Follow principle of least privilege
- Regular security audits

### Reporting Security Issues

Please report security vulnerabilities privately to the maintainers.

## 📋 Release Process

### Version Numbering

We use Semantic Versioning (SemVer):
- Major: Breaking changes
- Minor: New features (backward compatible)
- Patch: Bug fixes

### Release Checklist

- [ ] Update version numbers
- [ ] Update CHANGELOG.md
- [ ] Run full test suite
- [ ] Update documentation
- [ ] Create release notes
- [ ] Tag release in Git

## 🤔 Questions?

If you have questions about contributing:
1. Check existing issues and discussions
2. Create a new discussion topic
3. Reach out to maintainers

Thank you for contributing to make this project better for everyone!
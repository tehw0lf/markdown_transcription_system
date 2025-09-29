# Troubleshooting Guide

This guide covers common issues and solutions for the Universal Markdown Audio Transcription System.

## 🔧 Quick Diagnostics

### 🧪 Automated Test Suite (Recommended)

**First, try the comprehensive test script:**

```bash
# Run the automated test suite (safe - creates isolated environment)
./test_system.sh

# This will:
# - Test all system components
# - Create detailed test report
# - Identify issues automatically
# - Test with sample data safely
```

If the test script reveals issues, continue with manual diagnostics below.

### System Health Check

```bash
# Check Python version
python3 --version

# Check if Whisper is installed (system-wide command)
whisper --help

# Check FFmpeg
ffmpeg -version

# Check disk space
df -h

# Check available memory
free -h
```

### Configuration Validation

```bash
# Test configuration loading
python -m src.transcription_system --config config.yaml --help

# Validate configuration file
python -c "
import yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
    print('Configuration valid')
"
```

## 🚨 Common Issues

### 1. Installation Problems

#### "Whisper is not installed" Error

**Symptoms:**
```
Error: Whisper is not installed! Install with: sudo apt install python-openai-whisper OR pip install --global openai-whisper
```

**Solutions:**
```bash
# Recommended: Package manager installation (Ubuntu/Debian)
sudo apt install python-openai-whisper

# Alternative: Global pip installation
pip install --global openai-whisper

# Force reinstall (global)
pip uninstall openai-whisper
pip install --global openai-whisper

# Install specific version (global)
pip install --global openai-whisper==20231117
```

**Alternative: Manual Installation:**
```bash
# Install from source
git clone https://github.com/openai/whisper.git
cd whisper
pip install -e .
```

#### "FFmpeg not found" Error

**Symptoms:**
```
ffmpeg: command not found
```

**Solutions:**

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**CentOS/RHEL/Fedora:**
```bash
# CentOS/RHEL
sudo yum install ffmpeg

# Fedora
sudo dnf install ffmpeg
```

**macOS:**
```bash
# Using Homebrew
brew install ffmpeg

# Using MacPorts
sudo port install ffmpeg
```

**Windows:**
1. Download from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to PATH

**Verification:**
```bash
ffmpeg -version
which ffmpeg
```

### 2. Configuration Issues

#### "Configuration file not found" Error

**Symptoms:**
```
ConfigurationError: Configuration file not found: config.yaml
```

**Solutions:**
```bash
# Create example configuration
python -m src.transcription_system --create-config config.yaml --config-type obsidian

# Check file exists
ls -la config.yaml

# Use absolute path
python -m src.transcription_system --config /full/path/to/config.yaml
```

#### "Vault path does not exist" Error

**Symptoms:**
```
ConfigurationError: Vault path does not exist: /path/to/vault
```

**Solutions:**
```bash
# Create the directory
mkdir -p /path/to/vault

# Check permissions
ls -ld /path/to/vault

# Fix permissions
chmod 755 /path/to/vault
```

#### "Template file not found" Error

**Symptoms:**
```
ConfigurationError: Template file not found: templates/transcript-template.md
```

**Solutions:**
```bash
# Check template exists
ls -la templates/

# Create missing template
mkdir -p templates
cp examples/templates/* templates/

# Use absolute path in config
transcript_template_path: "/full/path/to/templates/transcript-template.md"
```

### 3. Permission Issues

#### "Permission denied" Errors

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied: '/path/to/file'
```

**Solutions:**
```bash
# Check file permissions
ls -la /path/to/file

# Fix file permissions
chmod 644 /path/to/file

# Fix directory permissions
chmod 755 /path/to/directory

# Change ownership
sudo chown $USER:$USER /path/to/file

# For log files
mkdir -p ~/.local/share/markdown-transcription
chmod 755 ~/.local/share/markdown-transcription
```

#### "Lock file" Issues

**Symptoms:**
```
Another instance is already running
```

**Solutions:**
```bash
# Check for running processes
ps aux | grep transcription

# Remove stale lock file
rm -f /var/lock/markdown-transcription.lock

# Or use user-specific lock file
lock_file: "/tmp/markdown-transcription-$USER.lock"
```

### 4. Performance Issues

#### Slow Transcription

**Symptoms:**
- Transcription takes very long
- High CPU/GPU usage
- System becomes unresponsive

**Solutions:**
```yaml
# Use smaller model
whisper_model: "tiny"  # or "base", "small"

# Reduce batch size (if processing multiple files)
# Process one file at a time
```

**System optimization:**
```bash
# Check system resources
htop
nvidia-smi  # If using GPU

# Close unnecessary applications
# Increase swap space if needed
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### High Memory Usage

**Symptoms:**
- Out of memory errors
- System freezing
- Swap thrashing

**Solutions:**
```yaml
# Use smaller model
whisper_model: "tiny"

# Process files individually
# Enable aggressive cleanup
```

```bash
# Monitor memory usage
watch -n 1 free -h

# Increase swap space
sudo swapon --show
sudo fallocate -l 8G /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 5. Audio Processing Issues

#### "Unsupported audio format" Error

**Symptoms:**
```
Error: Could not process audio file
```

**Solutions:**
```bash
# Check file format
file audio.mp3
ffprobe audio.mp3

# Convert to supported format
ffmpeg -i input.aac -c:a libmp3lame output.mp3
ffmpeg -i input.wma -c:a libmp3lame output.mp3

# Add extension to config
audio_extensions: [".mp3", ".wav", ".m4a", ".aac", ".wma"]
```

#### "Corrupted audio file" Error

**Symptoms:**
```
Error: Invalid audio data
```

**Solutions:**
```bash
# Check file integrity
ffmpeg -v error -i audio.mp3 -f null -

# Repair audio file
ffmpeg -i corrupted.mp3 -c copy repaired.mp3

# Check file size
ls -lh audio.mp3
```

#### Empty Transcription Results

**Symptoms:**
- Transcription completes but produces empty text
- No error messages

**Solutions:**
```bash
# Check audio quality
ffprobe -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 audio.mp3

# Test with different model
whisper_model: "medium"

# Check audio has speech
# Play audio file to verify content
```

### 6. Text Processing Issues

#### "Encoding errors" 

**Symptoms:**
```
UnicodeDecodeError: 'utf-8' codec can't decode
```

**Solutions:**
```yaml
# Try different encoding
encoding: "utf-8"
# or
encoding: "latin-1"
```

```bash
# Check file encoding
file -bi filename.md

# Convert file encoding
iconv -f ISO-8859-1 -t UTF-8 input.md > output.md
```

#### "Link not added to notes"

**Symptoms:**
- Transcription succeeds but links aren't added to notes
- No error messages

**Solutions:**
```bash
# Check link format
grep -r "audio_filename" /path/to/notes/

# Verify audio embed pattern
grep -r "!\[\[.*\.mp3\]\]" /path/to/notes/

# Check transcript exists
ls -la transcripts/
```

### 7. System Service Issues

#### Systemd Service Not Starting

**Symptoms:**
```
Job for markdown-transcription.service failed
```

**Solutions:**
```bash
# Check service status
sudo systemctl status markdown-transcription.service

# Check logs
sudo journalctl -u markdown-transcription.service -f

# Check service file
sudo systemctl cat markdown-transcription.service

# Reload systemd
sudo systemctl daemon-reload
sudo systemctl restart markdown-transcription.service
```

#### Timer Not Triggering

**Symptoms:**
- Timer is active but service doesn't run
- No processing occurs

**Solutions:**
```bash
# Check timer status
sudo systemctl list-timers markdown-transcription.timer

# Check timer configuration
sudo systemctl cat markdown-transcription.timer

# Restart timer
sudo systemctl restart markdown-transcription.timer
```

### 8. Network and Storage Issues

#### "Disk full" Errors

**Symptoms:**
```
OSError: [Errno 28] No space left on device
```

**Solutions:**
```bash
# Check disk usage
df -h
du -sh /path/to/vault

# Clean up temporary files
rm -rf /tmp/markdown-transcription/*

# Clean up old logs
journalctl --vacuum-size=100M

# Move files to different disk
```

#### Network Storage Issues

**Symptoms:**
- Slow processing on network drives
- Permission errors on mounted drives

**Solutions:**
```bash
# Check mount options
mount | grep /path/to/vault

# Remount with better options
sudo mount -o remount,rw,user /path/to/vault

# Use local temp directory
temp_dir: "/tmp/markdown-transcription"
```

## 🔍 Advanced Diagnostics

### Enable Debug Mode

```yaml
# In config.yaml
log_level: "DEBUG"
console_logging: true
file_logging: true
```

### Trace Execution

```bash
# Run with Python tracing
python -m trace --trace src/transcription_system.py --config config.yaml

# Profile performance
python -m cProfile -o profile.stats src/transcription_system.py
```

### Check Dependencies

```bash
# List all installed packages
pip list

# Check for conflicts
pip check

# Verify specific versions
pip show openai-whisper
pip show torch
```

## 📋 Diagnostic Script

Create a diagnostic script to gather system information:

```bash
#!/bin/bash
# diagnostic.sh - Gather system information

echo "=== System Diagnostics ==="
echo "Date: $(date)"
echo "User: $USER"
echo "Working Directory: $(pwd)"
echo ""

echo "=== Python Environment ==="
python3 --version
which python3
echo ""

echo "=== Dependencies ==="
whisper --help >/dev/null 2>&1 && echo "Whisper: OK" || echo "Whisper: MISSING"
python3 -c "import yaml; print('PyYAML: OK')" 2>/dev/null || echo "PyYAML: MISSING"
ffmpeg -version 2>/dev/null | head -1 || echo "FFmpeg: MISSING"
echo ""

echo "=== System Resources ==="
free -h
df -h
echo ""

echo "=== File Permissions ==="
ls -la config.yaml 2>/dev/null || echo "config.yaml: NOT FOUND"
ls -ld templates/ 2>/dev/null || echo "templates/: NOT FOUND"
echo ""

echo "=== Process Information ==="
ps aux | grep -E "(whisper|transcription)" | grep -v grep
echo ""

echo "=== Log Files ==="
find ~/.local/share/markdown-transcription -name "*.log" -exec ls -la {} \; 2>/dev/null || echo "No log files found"
```

## 🆘 Getting Help

If you can't resolve the issue:

1. **Check the logs** - Look for error messages in:
   - Console output
   - Log files (`~/.local/share/markdown-transcription/`)
   - System logs (`journalctl`)

2. **Run diagnostics** - Use the diagnostic script above

3. **Search existing issues** - Check GitHub issues for similar problems

4. **Create a new issue** - Include:
   - Error messages
   - Configuration file (remove sensitive data)
   - System information
   - Steps to reproduce

5. **Ask for help** - Use GitHub Discussions for questions

## 📞 Support Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and community help
- **Documentation**: Check README.md and docs/
- **Wiki**: Community-maintained solutions

Remember: The more information you provide, the faster we can help solve your issue!
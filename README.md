# Universal Markdown Audio Transcription System

A professional, **completely local and private** audio transcription system that works with any markdown-based note-taking application. Transform your audio recordings into searchable markdown transcripts without sending your data to the cloud.

## 🚀 Key Features

- **🔒 100% Local & Private** - Audio never leaves your machine
- **💰 Zero Ongoing Costs** - No API keys or subscription fees
- **📱 Universal Compatibility** - Works with Obsidian, Logseq, Foam, Zettlr, and any markdown system
- **🛡️ Security-First** - External script approach, no plugins required
- **📄 Template-Driven** - Customizable output formats
- **🎯 Smart Linking** - Automatically adds transcript links to existing notes
- **⚡ Batch Processing** - Handle multiple files efficiently
- **🎨 Configurable** - JSON/YAML configuration with multiple profiles

## 📋 Quick Start

### 1. Install Dependencies

```bash
# Install system dependencies (required: ffmpeg for audio processing)
# Ubuntu/Debian:
sudo apt update && sudo apt install ffmpeg

# macOS with Homebrew:
brew install ffmpeg

# Arch Linux:
sudo pacman -S ffmpeg

# Install Python dependencies using UV (recommended)
uv sync

# Alternative: Use the installation script
chmod +x scripts/install.sh && ./scripts/install.sh
```

### 2. Create Configuration

```bash
# Create example configuration for your markdown system
uv run python -m src.transcription_system --create-config config.yaml --config-type obsidian

# Or create for other systems
uv run python -m src.transcription_system --create-config config.yaml --config-type logseq
uv run python -m src.transcription_system --create-config config.yaml --config-type foam
```

### 3. Edit Configuration

Edit `config.yaml` to match your setup:

```yaml
# Basic configuration
vault_path: "/path/to/your/notes"
audio_folder_name: "Audio"
transcripts_folder_name: "Audio-Transcripts"

# Whisper settings
whisper_model: "medium"  # tiny, base, small, medium, large
language: "auto"         # or specify: en, de, fr, es, etc.

# Link format (adjust for your markdown system)
link_format_style: "wikilink"  # wikilink, standard, or custom
link_format_prefix: "📝 **Transcript:**"
```

### 4. Test the System (Recommended)

```bash
# Run comprehensive test suite (safe - creates isolated test environment)
./test_system.sh

# The test will:
# - Create a temporary test environment using uv
# - Test all system components safely
# - Generate a detailed test report
# - Optionally test actual transcription with sample audio
```

### 5. Run Transcription

```bash
# Run with your configuration
uv run python -m src.transcription_system --config config.yaml
```

## 🧪 Testing

Before using the system on your actual files, it's highly recommended to run the test suite:

### Comprehensive Test Suite

The included test script provides safe, isolated testing:

```bash
# Make the test script executable (if not already)
chmod +x test_system.sh

# Run the test suite
./test_system.sh
```

**What the test does:**
- ✅ Creates isolated test directory with timestamp
- ✅ Uses `uv` for clean virtual environment
- ✅ Tests all system components without affecting your files
- ✅ Creates sample audio and markdown files for testing
- ✅ Generates detailed test report
- ✅ Optional real transcription test with tiny model

**Test Components:**
1. **Import Tests** - Verifies code loads correctly
2. **Configuration Tests** - Tests config creation and validation
3. **System Tests** - Tests main system initialization
4. **Template Tests** - Tests template loading
5. **File Discovery** - Tests finding audio files and notes
6. **Integration Tests** - Tests complete workflow
7. **Optional Transcription** - Real transcription with sample audio

### Manual Testing

If you prefer manual testing:

```bash
# Test configuration creation
python -m src.transcription_system --create-config test-config.yaml --config-type obsidian

# Test with dry-run on a copy of your vault
cp -r /path/to/your/vault /tmp/test-vault
# Edit test-config.yaml to point to /tmp/test-vault
python -m src.transcription_system --config test-config.yaml
```

## 🔧 Installation

### Option 1: Direct Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/markdown-audio-transcription.git
cd markdown-audio-transcription

# Install dependencies
pip install -r requirements.txt

# Install Whisper and system dependencies
# Ubuntu/Debian (recommended):
sudo apt install python-openai-whisper ffmpeg

# macOS:
brew install ffmpeg
pip install --global openai-whisper

# Windows:
# Download ffmpeg from https://ffmpeg.org/download.html
# pip install --global openai-whisper
```

### Option 2: Using the Install Script

```bash
# Run the installation script
chmod +x scripts/install.sh
./scripts/install.sh
```

## 📊 Supported Markdown Systems

### Obsidian
- **Link Format**: `[[transcript_name]]`
- **Audio Folder**: `Audio/`
- **Transcript Folder**: `Audio-Transcripts/`

### Logseq
- **Link Format**: `[[transcript_name]]`
- **Audio Folder**: `assets/`
- **Transcript Folder**: `transcripts/`

### Foam (VS Code)
- **Link Format**: `[transcript_name](transcript_name.md)`
- **Audio Folder**: `attachments/`
- **Transcript Folder**: `transcripts/`

### Zettlr
- **Link Format**: `[[transcript_name]]`
- **Audio Folder**: `media/`
- **Transcript Folder**: `transcripts/`

### Generic Markdown
- **Link Format**: `[transcript_name](transcript_name.md)`
- **Audio Folder**: `media/`
- **Transcript Folder**: `transcripts/`

## 🎛️ Configuration Options

### Basic Settings

```yaml
# Path to your notes/vault
vault_path: "/home/user/Notes"

# Folder names (relative to vault_path)
audio_folder_name: "Audio"
transcripts_folder_name: "Audio-Transcripts"

# Whisper AI settings
whisper_model: "medium"    # Model size affects accuracy vs speed
language: "auto"           # Auto-detect or specify (en, de, fr, etc.)

# Processing options
auto_move_files: true      # Move processed files to audio folder
create_timestamps: true    # Include detailed timestamps
skip_existing_transcripts: true  # Skip files that already have transcripts
recursive_search: true     # Search subdirectories for audio files
```

### Advanced Settings

```yaml
# Link format customization
link_format_style: "wikilink"  # wikilink, standard, or custom
link_format_prefix: "📝 **Transcript:**"

# File extensions to process
audio_extensions: [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac"]
video_extensions: [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm"]

# Logging configuration
log_level: "INFO"          # DEBUG, INFO, WARNING, ERROR
console_logging: true      # Log to console
file_logging: true         # Log to file
log_file: "/var/log/markdown-transcription.log"

# System settings
temp_dir: "/tmp"
lock_file: "/var/lock/markdown-transcription.lock"
encoding: "utf-8"
```

## 🎨 Template Customization

### Transcript Template

Edit `templates/transcript-template.md`:

```markdown
# Transcription: {filename}

**File:** `{filename}`  
**Date:** {date}  
**Original Location:** `{audio_folder}/{filename}`

## Transcript

{transcript_content}

## Detailed Timestamps

{timestamp_content}
```

### Link Template

Edit `templates/link-template.md`:

```markdown
📝 **Transcript:** [[{audio_name}_transcript]]
```

## 🛠️ Usage Examples

### Basic Usage

```bash
# Process all audio files in your vault
python -m src.transcription_system --config config.yaml
```

### Create Configurations

```bash
# Create Obsidian configuration
python -m src.transcription_system --create-config obsidian-config.yaml --config-type obsidian

# Create Logseq configuration
python -m src.transcription_system --create-config logseq-config.yaml --config-type logseq

# Create generic markdown configuration
python -m src.transcription_system --create-config generic-config.yaml --config-type generic
```

### Multiple Vaults

```bash
# Process different vaults with different configurations
python -m src.transcription_system --config work-vault.yaml
python -m src.transcription_system --config personal-vault.yaml
```

## 🔄 Automation

### Systemd Service (Linux)

Create automatic processing on file changes:

```bash
# Set up systemd service
sudo chmod +x scripts/setup-systemd.sh
sudo ./scripts/setup-systemd.sh

# Enable and start service
sudo systemctl enable markdown-transcription
sudo systemctl start markdown-transcription
```

### Cron Job

Process files periodically:

```bash
# Add to crontab (process every 30 minutes)
*/30 * * * * /usr/bin/python3 /path/to/transcription_system.py --config /path/to/config.yaml
```

### Directory Watching

Use with file system watchers like `inotify`:

```bash
# Watch for new audio files and process automatically
inotifywait -m -e create --format '%w%f' /path/to/vault/ | while read file; do
    if [[ $file =~ \.(mp3|wav|m4a)$ ]]; then
        python -m src.transcription_system --config config.yaml
    fi
done
```

## 🆚 Comparison with Alternatives

| Feature | This System | Whisper.cpp | Commercial APIs |
|---------|-------------|-------------|-----------------|
| **Privacy** | ✅ 100% Local | ✅ 100% Local | ❌ Cloud-based |
| **Cost** | ✅ Free | ✅ Free | ❌ Pay-per-use |
| **Markdown Integration** | ✅ Native | ❌ Manual | ❌ Manual |
| **Template System** | ✅ Built-in | ❌ None | ❌ None |
| **Auto-linking** | ✅ Automatic | ❌ Manual | ❌ Manual |
| **Multi-app Support** | ✅ Universal | ❌ Generic | ❌ Generic |
| **Batch Processing** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Accuracy** | ✅ High (Whisper) | ✅ High (Whisper) | ✅ High |

## 📈 Performance & Models

### Whisper Model Comparison

| Model | Speed | Accuracy | VRAM Usage | Best For |
|-------|-------|----------|------------|----------|
| `tiny` | Fastest | Good | ~1GB | Quick processing |
| `base` | Fast | Better | ~1GB | Balanced performance |
| `small` | Medium | Good | ~2GB | Most use cases |
| `medium` | Slower | Better | ~5GB | High accuracy needed |
| `large` | Slowest | Best | ~10GB | Maximum accuracy |

### Processing Times (Approximate)

- **10-minute audio file**:
  - `tiny`: ~30 seconds
  - `base`: ~1 minute
  - `small`: ~2 minutes
  - `medium`: ~4 minutes
  - `large`: ~8 minutes

## 🔍 Troubleshooting

### Common Issues

**1. "Whisper is not installed" error**
```bash
# Method 1 - Package manager (recommended for Ubuntu/Debian):
sudo apt install python-openai-whisper

# Method 2 - Global pip installation:
pip install --global openai-whisper
```

**2. "ffmpeg not found" error**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows: Download from https://ffmpeg.org/
```

**3. "Permission denied" errors**
```bash
# Fix file permissions
chmod +x scripts/*.sh
sudo chown -R $USER:$USER /path/to/vault
```

**4. "Another instance is already running"**
```bash
# Remove lock file if stale
sudo rm /var/lock/markdown-transcription.lock
```

**5. Template not found errors**
```bash
# Ensure templates directory exists
mkdir -p templates/
# Copy default templates from repository
```

### Performance Issues

**Slow transcription:**
- Use a smaller model (`tiny`, `base`, `small`)
- Close other applications to free up RAM/VRAM
- Consider using CPU-only mode for older hardware

**High memory usage:**
- Use smaller model
- Process files one at a time
- Increase system swap space

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/markdown-audio-transcription.git
cd markdown-audio-transcription

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run comprehensive test suite
./test_system.sh

# Run linting
flake8 src/
black src/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for the excellent speech recognition model
- The markdown note-taking community for inspiration and feedback
- All contributors who helped improve this system

## 📞 Support

- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/yourusername/markdown-audio-transcription/issues)
- **Discussions**: Ask questions and share ideas in [GitHub Discussions](https://github.com/yourusername/markdown-audio-transcription/discussions)
- **Documentation**: Find detailed guides in the [docs/](docs/) directory

---

**Made with ❤️ for the markdown note-taking community**
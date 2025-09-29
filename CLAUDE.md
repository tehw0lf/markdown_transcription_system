# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Universal Markdown Audio Transcription System - a privacy-first, local transcription tool that integrates with any markdown-based note-taking application (Obsidian, Logseq, Foam, Zettlr, etc.). The system uses OpenAI's Whisper model for high-quality local transcription without sending data to the cloud.

## Architecture

### Core Components

- **`src/transcription_system.py`** - Main transcription system class with file discovery, Whisper integration, and markdown generation
- **`src/config.py`** - Configuration management supporting JSON/YAML configs with validation and app-specific presets
- **`templates/`** - Customizable markdown templates for transcript output and link formatting

### Key Features

- **Template-driven output** - Configurable transcript and link templates
- **Universal markdown integration** - Works with any markdown app via configurable link formats
- **Smart file discovery** - Finds audio files and corresponding notes with regex-based pattern matching
- **Auto-linking** - Automatically adds transcript links to existing notes containing audio embeds
- **Multi-format support** - Audio and video files with extensive extension support
- **Lock mechanism** - Prevents multiple instances with file-based locking

## Development Commands

### Installation & Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Whisper and system dependencies (Ubuntu/Debian)
sudo apt install python-openai-whisper ffmpeg

# Alternative: Global pip installation
pip install --global openai-whisper

# Install using provided script
chmod +x scripts/install.sh && ./scripts/install.sh
```

### Testing

```bash
# Run comprehensive test suite (recommended - safe isolated testing)
./test_system.sh

# Manual testing with example config
python -m src.transcription_system --create-config test-config.yaml --config-type obsidian
python -m src.transcription_system --config test-config.yaml
```

### Usage

```bash
# Create configuration for different markdown apps
python -m src.transcription_system --create-config config.yaml --config-type obsidian
python -m src.transcription_system --create-config config.yaml --config-type logseq
python -m src.transcription_system --create-config config.yaml --config-type foam

# Run transcription
python -m src.transcription_system --config config.yaml

# Run as module from project root
python -m src.transcription_system --config /path/to/config.yaml
```

## Configuration Architecture

### Config Manager (`src/config.py`)

- **Multi-format support** - JSON and YAML configuration files
- **Validation system** - Validates paths, Whisper models, link formats, and extensions
- **App-specific presets** - Pre-configured templates for popular markdown apps
- **Path expansion** - Handles relative paths and template file resolution
- **Template loading** - Loads and validates markdown templates

### Link Format System

Three configurable link styles:
- `wikilink`: `[[transcript_name]]` (Obsidian, Logseq)
- `standard`: `[transcript_name](transcript_name.md)` (Foam, generic)
- `custom`: Uses template file for complex formatting

### Regex Pattern Generation

The system generates complex regex patterns for:
- Finding audio embeds in notes (multiple formats and folder structures)
- Adding transcript links after audio embeds
- Supporting both wikilink and standard markdown syntax

## File Processing Flow

1. **Discovery** - Find media files (recursive search optional)
2. **Validation** - Check for existing transcripts (skip if configured)
3. **Transcription** - Use Whisper with configured model and language
4. **Template Processing** - Generate markdown using configurable templates
5. **File Management** - Move processed files to audio folder (optional)
6. **Link Generation** - Find notes with audio references and add transcript links
7. **Ownership** - Fix file ownership if configured

## Testing Infrastructure

### Comprehensive Test Suite (`test_system.sh`)

- **Isolated testing** - Creates temporary environment with timestamp
- **UV integration** - Uses UV for clean virtual environment management
- **Multi-stage testing** - Import, config, system, template, discovery, and integration tests
- **Optional transcription** - Can test actual Whisper transcription with tiny model
- **Automatic cleanup** - Cleans up test environment and preserves test reports

### Test Components

1. Import validation
2. Configuration creation and loading
3. System initialization
4. Template loading
5. File and note discovery
6. Safe run testing (without transcription)
7. Optional real transcription testing

## Pre-commit Validation Commands

```bash
# Test the system safely before deployment
./test_system.sh

# For manual validation
python -c "from src.config import ConfigManager; from src.transcription_system import MarkdownTranscriptionSystem; print('✅ Imports successful')"
```

## Key Dependencies

- **whisper (system-wide)** - Core transcription engine (installed via package manager or global pip)
- **PyYAML** - Configuration file support
- **torch/torchaudio** - ML backend for Whisper
- **ffmpeg-python** - Audio/video processing

## Security Considerations

- **Local processing only** - No cloud API calls
- **File locking** - Prevents concurrent execution issues
- **Path validation** - Validates configuration paths
- **Error handling** - Comprehensive error handling and logging
- **Ownership management** - Optional file ownership fixing for multi-user systems
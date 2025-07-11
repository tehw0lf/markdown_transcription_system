# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-07-12

### Added
- Initial release of Universal Markdown Audio Transcription System
- Automatic audio transcription using OpenAI Whisper
- Support for multiple markdown note-taking systems:
  - Obsidian
  - Logseq
  - Foam
  - Generic markdown workflows
- Configurable templates for transcripts and links
- Comprehensive configuration system with YAML support
- File organization with automatic audio file management
- Cross-platform compatibility with uv package manager
- Lock file management for safe concurrent operation
- Comprehensive test suite (`test_system.sh`) with automatic cleanup
- Support for multiple audio and video formats
- Recursive file discovery
- Template-based transcript generation
- Automatic linking back to original notes
- Detailed logging and error handling
- Example configurations for different workflows
- Installation and setup scripts

### Features
- **Audio/Video Support**: .mp3, .wav, .m4a, .flac, .ogg, .aac, .wma, .mp4, .mkv, .avi, .mov, .wmv, .flv, .webm
- **Multiple Whisper Models**: Support for tiny, base, small, medium, large models
- **Flexible Configuration**: YAML-based configuration with environment-specific templates
- **Safe Operation**: Lock file management prevents concurrent runs
- **Template System**: Customizable transcript and link templates
- **Batch Processing**: Process multiple files in one run
- **Skip Existing**: Option to skip already transcribed files
- **Auto-move Files**: Organize audio files into designated folders
- **Timestamp Support**: Optional timestamp generation in transcripts

### Documentation
- Comprehensive README with setup instructions
- Configuration examples for different workflows
- Troubleshooting guide
- Security and contributing guidelines
- Testing documentation

### Technical Details
- Python 3.9+ compatibility
- Uses uv for fast package management
- FFmpeg integration for audio processing
- Robust error handling and logging
- Cross-platform file path handling
- Unicode support for international content
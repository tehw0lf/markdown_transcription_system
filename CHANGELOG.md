# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.4] - 2026-08-21

### Fixed
- Template rendering no longer discards a completed transcript when a template
  contains an unknown placeholder or a literal brace. `str.format` raised
  `KeyError`/`ValueError` in those cases, after Whisper had already done the
  work.
- `check_dependencies()` can now actually run: Whisper is imported lazily, so a
  missing installation produces the intended message instead of an `ImportError`
  at module import.
- A failed lock acquisition no longer leaves the lock file handle open, and
  `release_lock()` is idempotent.
- Lock contention (`EAGAIN`/`EACCES`) is distinguished from real `flock()`
  failures, which were previously all reported as "Another instance is already
  running".
- A custom link template that is missing or empty now falls back to a wikilink
  with a warning, instead of failing silently through a bare `except`.
- `test_system.sh` can be invoked from any working directory.

### Changed
- Whisper is no longer imported at module level, which keeps torch out of runs
  that never transcribe.

### Removed
- `create_markdown_transcript()`, an unreferenced duplicate of
  `create_markdown_transcript_from_result()`.

### Added
- Unit test suite (77 tests) covering template rendering, configuration,
  transcript generation, media discovery, note linking, locking and the
  dependency check.
- Lint (ruff) and unit tests run as part of `test_system.sh`, and therefore CI.

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
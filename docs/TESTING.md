# Testing Guide

This guide covers testing the Universal Markdown Audio Transcription System before using it on your actual files.

## 🧪 Comprehensive Test Suite

The system includes a comprehensive test script that safely tests all components without affecting your actual files.

### Quick Start

```bash
# Run the test suite
./test_system.sh

# The test creates an isolated environment and tests everything safely
```

### What the Test Suite Does

#### 🔒 **Safe Testing Environment**
- Creates timestamped test directory (`test_transcription_YYYYMMDD_HHMMSS/`)
- Uses `uv` to create isolated virtual environment
- Tests with sample data only - **your files are never touched**
- Automatically cleans up temporary files

#### 📋 **Test Components**

**1. Environment Setup**
- ✅ Checks `uv` availability
- ✅ Creates test directory structure
- ✅ Sets up virtual environment
- ✅ Installs dependencies

**2. Code Validation**
- ✅ **Import Tests** - Verifies all modules load correctly
- ✅ **Configuration Tests** - Tests config creation and validation
- ✅ **System Initialization** - Tests main class creation
- ✅ **Template Loading** - Tests template system

**3. Functionality Tests**
- ✅ **File Discovery** - Tests finding audio files
- ✅ **Note Discovery** - Tests finding markdown notes with audio
- ✅ **Pattern Matching** - Tests audio embed detection
- ✅ **Lock Management** - Tests file locking system

**4. Integration Tests**
- ✅ **End-to-End Setup** - Tests complete system initialization
- ✅ **Configuration Validation** - Tests with realistic config
- ✅ **Safe Run** - Tests system without actual transcription

**5. Optional Transcription Test**
- 🎵 **Sample Audio Creation** - Creates 5-second test tone
- 📝 **Test Note Creation** - Creates markdown note with audio reference
- 🔊 **Real Transcription** - Optional test with tiny Whisper model
- 🔗 **Link Integration** - Tests automatic link addition

### Test Output

The test suite generates:

#### 📊 **Test Report** (`test-report.md`)
```markdown
# Test Report

**Date:** 2024-01-15 14:30:22
**Test Directory:** /path/to/test_transcription_20240115_143022

## Test Results
### ✅ Passed Tests
- Basic imports ✓
- Configuration creation ✓
- System initialization ✓
- Template loading ✓
- File discovery ✓
- Integration tests ✓

### 📋 System Information
- Python Version: 3.11.6
- uv Version: 0.1.18
- FFmpeg Available: Yes
- Test Audio Created: Yes
```

#### 🔧 **Working Configuration** (`working-config.yaml`)
```yaml
# Ready-to-use configuration file
vault_path: "/path/to/test-vault"
whisper_model: "tiny"  # Small model for testing
# ... other settings
```

#### 🎵 **Test Files Created**
- `test-vault/test-audio.mp3` - Sample audio file
- `test-vault/notes/test-note.md` - Test markdown note
- `test-vault/Audio/` - Audio folder
- `test-vault/Audio-Transcripts/` - Transcripts folder

## 🎯 Test Scenarios

### Scenario 1: Basic Validation
```bash
# Quick validation without transcription
./test_system.sh
# Answer 'n' when asked about transcription test
```

**Use when:**
- First time setup
- Checking if system works
- Validating installation

### Scenario 2: Full Integration Test
```bash
# Complete test including transcription
./test_system.sh
# Answer 'y' when asked about transcription test
```

**Use when:**
- Before first real use
- After system updates
- Validating Whisper installation

### Scenario 3: Performance Test
```bash
# Test with larger audio file
./test_system.sh
# Then copy a longer audio file to test-vault/
# Run transcription test
```

**Use when:**
- Testing system performance
- Validating with real audio length
- Checking resource usage

## 🔍 Understanding Test Results

### ✅ All Tests Pass
```
🎉 Test Suite Complete!
All tests completed successfully!
```

**What this means:**
- System is ready for use
- All dependencies are working
- Configuration system is functional
- Templates are loading correctly

**Next steps:**
1. Copy `working-config.yaml` to your desired location
2. Edit paths to point to your actual vault
3. Test with one small audio file first

### ⚠️ Some Tests Fail
```
❌ Import error: No module named 'whisper'
❌ Configuration error: Vault path does not exist
```

**Common issues and solutions:**

**Missing Dependencies:**
```bash
# Install missing dependencies
uv pip install openai-whisper
# or
pip install -r requirements.txt
```

**Configuration Issues:**
```bash
# Check paths in configuration
# Make sure directories exist
# Check file permissions
```

**Template Issues:**
```bash
# Ensure templates directory exists
mkdir -p templates/
# Copy default templates
cp examples/templates/* templates/
```

## 🛠️ Manual Testing

If you prefer manual testing or need to debug specific issues:

### Test 1: Basic Import
```bash
python -c "
import sys
sys.path.insert(0, 'src')
from src.config import ConfigManager
from src.transcription_system import MarkdownTranscriptionSystem
print('✅ All imports successful')
"
```

### Test 2: Configuration
```bash
# Create test configuration
python -m src.transcription_system --create-config test.yaml --config-type obsidian

# Test loading
python -c "
from src.config import ConfigManager
config = ConfigManager('test.yaml')
print('✅ Configuration loaded')
"
```

### Test 3: System Initialization
```bash
python -c "
from src.config import ConfigManager
from src.transcription_system import MarkdownTranscriptionSystem
config = ConfigManager('test.yaml')
system = MarkdownTranscriptionSystem(config)
print('✅ System initialized')
"
```

### Test 4: File Discovery
```bash
# Create test structure
mkdir -p test-vault/{Audio,notes}
touch test-vault/test.mp3
echo '![[test.mp3]]' > test-vault/notes/note.md

# Test discovery
python -c "
from src.config import ConfigManager
from src.transcription_system import MarkdownTranscriptionSystem
config = ConfigManager('test.yaml')
system = MarkdownTranscriptionSystem(config)
files = system.find_media_files()
notes = system.find_notes_with_audio('test')
print(f'Found {len(files)} files, {len(notes)} notes')
"
```

## 🚀 Performance Testing

### CPU/Memory Usage
```bash
# Monitor during test
htop &
./test_system.sh
# Answer 'y' for transcription test
```

### Different Models
```bash
# Test with different Whisper models
# Edit working-config.yaml:
whisper_model: "tiny"    # Fastest, lower accuracy
whisper_model: "base"    # Balanced
whisper_model: "small"   # Better accuracy
whisper_model: "medium"  # High accuracy
```

### Large Files
```bash
# Test with longer audio
cp /path/to/longer-audio.mp3 test-vault/
# Run transcription test
```

## 🔧 Troubleshooting Tests

### Test Script Won't Run
```bash
# Check if executable
ls -la test_system.sh
# Make executable
chmod +x test_system.sh

# Check uv installation
uv --version
# Install if missing
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Tests Fail to Start
```bash
# Check Python version
python3 --version
# Ensure Python 3.8+

# Check directory structure
ls -la src/
# Should contain transcription_system.py and config.py
```

### FFmpeg Issues
```bash
# Test FFmpeg
ffmpeg -version
# Install if missing (Ubuntu/Debian)
sudo apt install ffmpeg
```

### Virtual Environment Issues
```bash
# Clean up and retry
rm -rf test_transcription_*/
./test_system.sh
```

## 📋 Test Checklist

Before using the system on real data:

- [ ] Test script runs without errors
- [ ] All 10 test components pass
- [ ] Configuration creates successfully
- [ ] System initializes without errors
- [ ] Templates load correctly
- [ ] File discovery works
- [ ] Optional: Transcription test passes
- [ ] Test report generated
- [ ] Working configuration available

## 📞 Getting Help

If tests fail:

1. **Check the test report** - `test-report.md` contains detailed information
2. **Review test output** - Look for specific error messages
3. **Check dependencies** - Ensure all required packages are installed
4. **Verify system requirements** - Python 3.8+, FFmpeg, etc.
5. **Ask for help** - Create GitHub issue with test report attached

## 🎯 Next Steps

After successful testing:

1. **Copy working configuration**: `cp working-config.yaml my-config.yaml`
2. **Edit paths**: Update `vault_path` to your actual notes directory
3. **Test with one file**: Place one small audio file in your vault
4. **Run real transcription**: `python -m src.transcription_system --config my-config.yaml`
5. **Verify results**: Check transcripts folder and note links

Remember: The test environment is completely isolated and safe - your actual files are never touched during testing!
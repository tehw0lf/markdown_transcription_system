#!/bin/bash

# Universal Markdown Audio Transcription System - Test Script
# This script safely tests the system without affecting your actual files

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Cleanup function
cleanup_test_directory() {
    if [ -n "$TEST_DIR" ] && [ -n "$ORIGINAL_DIR" ]; then
        print_step "Cleaning up test directory..."
        
        # Go back to original directory
        cd "$ORIGINAL_DIR"
        
        # Move test summary to original directory if it exists
        if [ -f "$TEST_DIR/test-report.md" ]; then
            mv "$TEST_DIR/test-report.md" "./test-report-$(date +%Y%m%d_%H%M%S).md"
            print_success "Test summary saved to: test-report-$(date +%Y%m%d_%H%M%S).md"
        fi
        
        # Remove the test directory
        rm -rf "$TEST_DIR"
        print_success "Test directory cleaned up"
    fi
}

# Set up trap to ensure cleanup happens on script exit
trap cleanup_test_directory EXIT

echo "🧪 Universal Markdown Audio Transcription System - Test Suite"
echo "============================================================="
echo ""

# Check if uv is available
if ! command -v uv &> /dev/null; then
    print_error "uv is not installed. Please install it first:"
    print_error "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

print_info "Found uv: $(uv --version)"

# Store original directory
ORIGINAL_DIR="$(pwd)"

# Create test directory
TEST_DIR="test_transcription_$(date +%Y%m%d_%H%M%S)"
print_step "Creating test directory: $TEST_DIR"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

# Create test vault structure
print_step "Creating test vault structure..."
mkdir -p test-vault/{Audio,Audio-Transcripts,notes}

# Create a test markdown note with audio reference
cat > test-vault/notes/test-note.md << 'EOF'
# Test Note

This is a test note for the transcription system.

![[test-audio.mp3]]

Some content after the audio file.
EOF

# Create a simple test audio file (using ffmpeg if available)
print_step "Creating test audio file..."
if command -v ffmpeg &> /dev/null; then
    # Create a 5-second test audio file with a simple tone
    ffmpeg -f lavfi -i "sine=frequency=440:duration=5" -ac 1 -ar 16000 test-vault/test-audio.mp3 -y &>/dev/null
    print_success "Created test audio file (5-second tone)"
else
    print_warning "ffmpeg not available - you'll need to manually add a test audio file"
    print_warning "Copy a small audio file to: test-vault/test-audio.mp3"
fi

# Copy project files to test directory
print_step "Copying project files..."
cp -r ../src .
cp -r ../templates .
cp -r ../examples .
cp ../requirements.txt .

# Create test virtual environment using uv
print_step "Creating virtual environment with uv..."
uv venv .venv
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    print_success "Virtual environment activated"
else
    print_error "Failed to create virtual environment"
    exit 1
fi

# Install dependencies
print_step "Installing dependencies with uv..."
uv pip install -r requirements.txt

# Test 1: Basic import test
print_step "Test 1: Testing basic imports..."
python -c "
import sys
sys.path.insert(0, 'src')
try:
    from src.config import ConfigManager
    from src.transcription_system import MarkdownTranscriptionSystem
    print('✅ All imports successful')
except Exception as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

# Test 2: Configuration creation test
print_step "Test 2: Testing configuration creation..."
python -m src.transcription_system --create-config test-config.yaml --config-type obsidian
if [ -f "test-config.yaml" ]; then
    print_success "Configuration file created successfully"
else
    print_error "Failed to create configuration file"
    exit 1
fi

# Test 3: Configuration validation test
print_step "Test 3: Testing configuration validation..."
python -c "
import sys
sys.path.insert(0, 'src')
from src.config import ConfigManager
try:
    # Test with default config
    config = ConfigManager()
    print('✅ Default configuration loaded')
    
    # Test with created config (modify paths to test directory)
    config = ConfigManager('test-config.yaml')
    print('✅ Test configuration loaded')
except Exception as e:
    print(f'❌ Configuration error: {e}')
    sys.exit(1)
"

# Test 4: Create working configuration
print_step "Test 4: Creating working test configuration..."
cat > working-config.yaml << EOF
# Working test configuration
vault_path: "$(pwd)/test-vault"
audio_folder_name: "Audio"
transcripts_folder_name: "Audio-Transcripts"
temp_dir: "$(pwd)/temp"

transcript_template_path: "templates/transcript-template.md"
link_template_path: "templates/link-template.md"

whisper_model: "tiny"  # Use smallest model for testing
language: "auto"

log_file: "$(pwd)/test.log"
lock_file: "$(pwd)/test.lock"
encoding: "utf-8"

audio_extensions: [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac", ".wma"]
video_extensions: [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"]

link_format_prefix: "📝 **Transcript:**"
link_format_style: "wikilink"

auto_move_files: true
create_timestamps: true
skip_existing_transcripts: true
recursive_search: true

log_level: "INFO"
console_logging: true
file_logging: true
EOF

# Also fix the test-config.yaml to use local paths
print_step "Test 4b: Fixing test configuration paths..."
sed -i "s|vault_path: .*|vault_path: \"$(pwd)/test-vault\"|g" test-config.yaml
sed -i "s|log_file: .*|log_file: \"$(pwd)/test.log\"|g" test-config.yaml
sed -i "s|lock_file: .*|lock_file: \"$(pwd)/test.lock\"|g" test-config.yaml
sed -i "s|temp_dir: .*|temp_dir: \"$(pwd)/temp\"|g" test-config.yaml

# Test 5: System initialization test
print_step "Test 5: Testing system initialization..."
python -c "
import sys
sys.path.insert(0, 'src')
from src.config import ConfigManager
from src.transcription_system import MarkdownTranscriptionSystem

try:
    config = ConfigManager('working-config.yaml')
    system = MarkdownTranscriptionSystem(config)
    print('✅ System initialized successfully')
    print(f'✅ Vault path: {system.vault_path}')
    print(f'✅ Audio folder: {system.audio_folder}')
    print(f'✅ Transcripts folder: {system.transcripts_folder}')
except Exception as e:
    print(f'❌ System initialization error: {e}')
    sys.exit(1)
"

# Test 6: Dependency check test
print_step "Test 6: Testing dependency checks..."
python -c "
import sys
sys.path.insert(0, 'src')
from src.config import ConfigManager
from src.transcription_system import MarkdownTranscriptionSystem

try:
    config = ConfigManager('working-config.yaml')
    system = MarkdownTranscriptionSystem(config)
    
    # Test whisper availability
    has_whisper = system.check_dependencies()
    if has_whisper:
        print('✅ Whisper is available')
    else:
        print('⚠️  Whisper is not available (expected for testing)')
    
    print('✅ Dependency check completed')
except Exception as e:
    print(f'❌ Dependency check error: {e}')
    sys.exit(1)
"

# Test 7: Template loading test
print_step "Test 7: Testing template loading..."
python -c "
import sys
sys.path.insert(0, 'src')
from src.config import ConfigManager
from src.transcription_system import MarkdownTranscriptionSystem

try:
    config = ConfigManager('working-config.yaml')
    system = MarkdownTranscriptionSystem(config)
    
    # Test template loading
    system.load_templates()
    print('✅ Templates loaded successfully')
    
    # Test template content
    if hasattr(system, 'transcript_template') and system.transcript_template:
        print('✅ Transcript template loaded')
    if hasattr(system, 'link_template') and system.link_template:
        print('✅ Link template loaded')
        
except Exception as e:
    print(f'❌ Template loading error: {e}')
    sys.exit(1)
"

# Test 8: File discovery test
print_step "Test 8: Testing file discovery..."
python -c "
import sys
sys.path.insert(0, 'src')
from src.config import ConfigManager
from src.transcription_system import MarkdownTranscriptionSystem

try:
    config = ConfigManager('working-config.yaml')
    system = MarkdownTranscriptionSystem(config)
    
    # Test file discovery
    media_files = system.find_media_files()
    print(f'✅ Found {len(media_files)} media files')
    
    for file in media_files:
        print(f'   - {file}')
        
except Exception as e:
    print(f'❌ File discovery error: {e}')
    sys.exit(1)
"

# Test 9: Note discovery test
print_step "Test 9: Testing note discovery..."
python -c "
import sys
sys.path.insert(0, 'src')
from src.config import ConfigManager
from src.transcription_system import MarkdownTranscriptionSystem

try:
    config = ConfigManager('working-config.yaml')
    system = MarkdownTranscriptionSystem(config)
    
    # Test note discovery
    notes = system.find_notes_with_audio('test-audio')
    print(f'✅ Found {len(notes)} notes with audio references')
    
    for note in notes:
        print(f'   - {note}')
        
except Exception as e:
    print(f'❌ Note discovery error: {e}')
    sys.exit(1)
"

# Test 10: Safe run test (without actual transcription)
print_step "Test 10: Testing safe run (dry-run mode)..."
python -c "
import sys
sys.path.insert(0, 'src')
from src.config import ConfigManager
from src.transcription_system import MarkdownTranscriptionSystem

try:
    config = ConfigManager('working-config.yaml')
    system = MarkdownTranscriptionSystem(config)
    
    # Test system setup without running transcription
    print('✅ System setup completed without errors')
    
    # Test that we can acquire/release locks
    if system.acquire_lock():
        print('✅ Lock acquired successfully')
        system.release_lock()
        print('✅ Lock released successfully')
    else:
        print('⚠️  Could not acquire lock (may be normal)')
        
except Exception as e:
    print(f'❌ Safe run error: {e}')
    sys.exit(1)
"

# Create a summary report
print_step "Creating test summary report..."
cat > test-report.md << EOF
# Test Report

**Date:** $(date)
**Test Directory:** $(pwd)

## Test Results

### ✅ Passed Tests
- Basic imports
- Configuration creation
- Configuration validation
- System initialization
- Dependency checks
- Template loading
- File discovery
- Note discovery
- Safe run test

### 📋 System Information
- Python Version: $(python --version)
- uv Version: $(uv --version)
- FFmpeg Available: $(command -v ffmpeg &> /dev/null && echo "Yes" || echo "No")
- Test Audio Created: $([ -f "test-vault/test-audio.mp3" ] && echo "Yes" || echo "No")

### 📁 Test Files Created
- Configuration: working-config.yaml
- Test Vault: test-vault/
- Test Audio: test-vault/test-audio.mp3
- Test Note: test-vault/notes/test-note.md
- Log File: test.log (if created)

### 🎯 Next Steps
1. If all tests passed, you can safely use the system
2. To test with real transcription, install whisper: \`uv pip install openai-whisper\`
3. Copy working-config.yaml and modify paths to your actual vault
4. Test with a small audio file first

### 🗂️ Files to Review
- Check working-config.yaml for your actual configuration
- Review test-vault/ structure for reference
- Look at test.log for any warnings or errors

EOF

# Final summary
echo ""
echo "🎉 Test Suite Complete!"
echo "======================="
echo ""
print_success "All tests completed successfully!"
print_info "Test directory: $(pwd)"
print_info "Test report: test-report.md"
print_info "Working config: working-config.yaml"
echo ""
print_info "Next steps:"
echo "  1. Review the test report: cat test-report.md"
echo "  2. Copy working-config.yaml and modify for your setup"
echo "  3. Test with a small audio file first"
echo "  4. Install whisper if you want to test transcription: uv pip install openai-whisper"
echo ""
print_warning "Remember: This test used a temporary environment"
print_warning "For real use, install dependencies in your main environment or create a dedicated one"
echo ""

# Ask if user wants to test transcription
if [ -f "test-vault/test-audio.mp3" ]; then
    print_step "Installing whisper for transcription test..."
    uv pip install openai-whisper
    
    print_step "Running transcription test..."
    python -m src.transcription_system --config working-config.yaml
    
    print_step "Checking results..."
    if [ -f "test-vault/Audio-Transcripts/test-audio_transcript.md" ]; then
        print_success "Transcription test successful!"
        print_info "Transcript created: test-vault/Audio-Transcripts/test-audio_transcript.md"
        
        # Show first few lines of transcript
        echo ""
        echo "📝 Transcript preview:"
        head -10 "test-vault/Audio-Transcripts/test-audio_transcript.md"
        echo ""
    else
        print_warning "Transcription test didn't create expected file"
    fi
    
    # Check if link was added to note
    if grep -q "test-audio_transcript" "test-vault/notes/test-note.md"; then
        print_success "Link successfully added to note!"
    else
        print_warning "Link was not added to note"
    fi
fi

echo ""
print_info "Test complete! Cleaning up test directory..."
cleanup_test_directory
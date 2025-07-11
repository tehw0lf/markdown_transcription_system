#!/bin/bash

# Universal Markdown Audio Transcription System - Installation Script
# This script installs the system and its dependencies

set -e

echo "🎯 Universal Markdown Audio Transcription System - Installation"
echo "=============================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]]; then
    OS="windows"
else
    print_error "Unsupported operating system: $OSTYPE"
    exit 1
fi

print_info "Detected OS: $OS"

# Check Python version
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_info "Python version: $PYTHON_VERSION"

# Check if Python version is >= 3.8
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    print_info "Python version is compatible"
else
    print_error "Python 3.8 or higher is required"
    exit 1
fi

# Install system dependencies
print_info "Installing system dependencies..."

if [[ "$OS" == "linux" ]]; then
    # Check if we have apt or yum
    if command -v apt-get &> /dev/null; then
        print_info "Using apt package manager"
        sudo apt-get update
        sudo apt-get install -y ffmpeg python3-pip python3-venv git
    elif command -v yum &> /dev/null; then
        print_info "Using yum package manager"
        sudo yum install -y ffmpeg python3-pip python3-venv git
    elif command -v dnf &> /dev/null; then
        print_info "Using dnf package manager"
        sudo dnf install -y ffmpeg python3-pip python3-venv git
    else
        print_warning "Could not detect package manager. Please install ffmpeg manually."
    fi
elif [[ "$OS" == "macos" ]]; then
    if command -v brew &> /dev/null; then
        print_info "Using Homebrew"
        brew install ffmpeg python3 git
    else
        print_warning "Homebrew not found. Please install ffmpeg manually."
        print_info "Install Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    fi
elif [[ "$OS" == "windows" ]]; then
    print_warning "Windows detected. Please ensure you have:"
    print_warning "1. FFmpeg installed and in PATH"
    print_warning "2. Python 3.8+ installed"
    print_warning "3. Git installed"
fi

# Create virtual environment
print_info "Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
print_info "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
print_info "Upgrading pip..."
python -m pip install --upgrade pip

# Install Python dependencies
print_info "Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
print_info "Creating directories..."
mkdir -p templates examples/config-examples scripts docs logs

# Set up configuration directory
CONFIG_DIR="$HOME/.config/markdown-transcription"
mkdir -p "$CONFIG_DIR"

# Copy example configurations
print_info "Copying example configurations..."
cp examples/config-examples/*.yaml "$CONFIG_DIR/"

# Create default configuration
print_info "Creating default configuration..."
cat > "$CONFIG_DIR/config.yaml" << EOF
# Default configuration for Universal Markdown Audio Transcription System
# Edit this file to match your setup

vault_path: "./vault"  # Change to your actual vault path
audio_folder_name: "Audio"
transcripts_folder_name: "Audio-Transcripts"
temp_dir: "/tmp"

transcript_template_path: "templates/transcript-template.md"
link_template_path: "templates/link-template.md"

whisper_model: "medium"
language: "auto"

log_file: "$HOME/.local/share/markdown-transcription/transcription.log"
lock_file: "/tmp/markdown-transcription.lock"
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

# Create log directory
mkdir -p "$HOME/.local/share/markdown-transcription"

# Create wrapper script
print_info "Creating wrapper script..."
cat > "$HOME/.local/bin/markdown-transcription" << EOF
#!/bin/bash
# Universal Markdown Audio Transcription System Wrapper Script

SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="\$(dirname "\$(dirname "\$SCRIPT_DIR")")"

# Find the project directory (look for src/transcription_system.py)
if [ -f "\$PROJECT_DIR/src/transcription_system.py" ]; then
    cd "\$PROJECT_DIR"
elif [ -f "\$HOME/markdown-audio-transcription/src/transcription_system.py" ]; then
    cd "\$HOME/markdown-audio-transcription"
else
    echo "Error: Could not find transcription system installation"
    exit 1
fi

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Run the transcription system
python -m src.transcription_system "\$@"
EOF

# Make wrapper script executable
chmod +x "$HOME/.local/bin/markdown-transcription"

# Add to PATH if not already there
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    print_info "Adding $HOME/.local/bin to PATH..."
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    if [[ "$OS" == "macos" ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
    fi
fi

# Test installation
print_info "Testing installation..."
if python -m src.transcription_system --help &> /dev/null; then
    print_info "✅ Installation successful!"
else
    print_error "❌ Installation test failed"
    exit 1
fi

# Installation complete
echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo ""
echo "Configuration files are in: $CONFIG_DIR"
echo "Default config: $CONFIG_DIR/config.yaml"
echo ""
echo "Usage:"
echo "  markdown-transcription --config $CONFIG_DIR/config.yaml"
echo "  markdown-transcription --create-config myconfig.yaml --config-type obsidian"
echo ""
echo "Next steps:"
echo "1. Edit the configuration file to match your setup"
echo "2. Run the system with your configuration"
echo "3. Check the README.md for detailed usage instructions"
echo ""
echo "For help: markdown-transcription --help"
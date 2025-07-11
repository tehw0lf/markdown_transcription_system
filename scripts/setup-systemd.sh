#!/bin/bash

# Universal Markdown Audio Transcription System - Systemd Service Setup
# This script sets up a systemd service for automatic transcription

set -e

echo "🔧 Universal Markdown Audio Transcription System - Systemd Setup"
echo "================================================================="

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
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

# Check if systemd is available
if ! command -v systemctl &> /dev/null; then
    print_error "systemd is not available on this system"
    exit 1
fi

# Get the user who called sudo
REAL_USER=${SUDO_USER:-$USER}
if [[ "$REAL_USER" == "root" ]]; then
    print_error "Please run this script as a regular user with sudo"
    exit 1
fi

REAL_HOME=$(eval echo ~$REAL_USER)
print_info "Setting up service for user: $REAL_USER"
print_info "Home directory: $REAL_HOME"

# Find the project directory
PROJECT_DIR=""
if [ -f "$REAL_HOME/markdown-audio-transcription/src/transcription_system.py" ]; then
    PROJECT_DIR="$REAL_HOME/markdown-audio-transcription"
elif [ -f "$(pwd)/src/transcription_system.py" ]; then
    PROJECT_DIR="$(pwd)"
else
    print_error "Could not find transcription system installation"
    print_error "Please run this script from the project directory"
    exit 1
fi

print_info "Project directory: $PROJECT_DIR"

# Default configuration path
DEFAULT_CONFIG="$REAL_HOME/.config/markdown-transcription/config.yaml"

# Ask for configuration file
read -p "Configuration file path [$DEFAULT_CONFIG]: " CONFIG_FILE
CONFIG_FILE=${CONFIG_FILE:-$DEFAULT_CONFIG}

if [ ! -f "$CONFIG_FILE" ]; then
    print_error "Configuration file not found: $CONFIG_FILE"
    exit 1
fi

print_info "Using configuration: $CONFIG_FILE"

# Ask for service type
echo "Select service type:"
echo "1. Timer-based (run periodically)"
echo "2. Path-based (run when files change)"
echo "3. One-shot (run once)"
read -p "Enter choice [1-3]: " SERVICE_TYPE

case $SERVICE_TYPE in
    1)
        SERVICE_MODE="timer"
        ;;
    2)
        SERVICE_MODE="path"
        ;;
    3)
        SERVICE_MODE="oneshot"
        ;;
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

# Create service file
SERVICE_FILE="/etc/systemd/system/markdown-transcription.service"

print_info "Creating service file: $SERVICE_FILE"

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Universal Markdown Audio Transcription System
After=network.target

[Service]
Type=oneshot
User=$REAL_USER
Group=$REAL_USER
WorkingDirectory=$PROJECT_DIR
Environment=HOME=$REAL_HOME
Environment=USER=$REAL_USER
ExecStart=$PROJECT_DIR/.venv/bin/python -m src.transcription_system --config $CONFIG_FILE
StandardOutput=journal
StandardError=journal
SyslogIdentifier=markdown-transcription

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=false
ReadWritePaths=$REAL_HOME
ReadWritePaths=/tmp
ReadWritePaths=/var/log

[Install]
WantedBy=multi-user.target
EOF

# Create timer file if timer-based
if [[ "$SERVICE_MODE" == "timer" ]]; then
    TIMER_FILE="/etc/systemd/system/markdown-transcription.timer"
    
    echo "Timer configuration:"
    echo "1. Every 5 minutes"
    echo "2. Every 15 minutes"
    echo "3. Every 30 minutes"
    echo "4. Every hour"
    echo "5. Custom"
    read -p "Enter choice [1-5]: " TIMER_CHOICE
    
    case $TIMER_CHOICE in
        1) TIMER_SPEC="*:0/5" ;;
        2) TIMER_SPEC="*:0/15" ;;
        3) TIMER_SPEC="*:0/30" ;;
        4) TIMER_SPEC="hourly" ;;
        5) 
            read -p "Enter systemd timer specification: " TIMER_SPEC
            ;;
        *) 
            print_error "Invalid choice"
            exit 1
            ;;
    esac
    
    print_info "Creating timer file: $TIMER_FILE"
    
    cat > "$TIMER_FILE" << EOF
[Unit]
Description=Universal Markdown Audio Transcription System Timer
Requires=markdown-transcription.service

[Timer]
OnCalendar=$TIMER_SPEC
Persistent=true

[Install]
WantedBy=timers.target
EOF
fi

# Create path file if path-based
if [[ "$SERVICE_MODE" == "path" ]]; then
    PATH_FILE="/etc/systemd/system/markdown-transcription.path"
    
    # Read vault path from config
    VAULT_PATH=$(grep "vault_path:" "$CONFIG_FILE" | sed 's/.*: *"\?\([^"]*\)"\?.*/\1/')
    if [ -z "$VAULT_PATH" ]; then
        print_error "Could not read vault_path from configuration"
        exit 1
    fi
    
    # Expand user path
    VAULT_PATH=$(eval echo "$VAULT_PATH")
    
    print_info "Creating path file: $PATH_FILE"
    print_info "Watching directory: $VAULT_PATH"
    
    cat > "$PATH_FILE" << EOF
[Unit]
Description=Universal Markdown Audio Transcription System Path Monitor
Requires=markdown-transcription.service

[Path]
PathModified=$VAULT_PATH
Unit=markdown-transcription.service

[Install]
WantedBy=multi-user.target
EOF
fi

# Reload systemd
print_info "Reloading systemd..."
systemctl daemon-reload

# Enable and start the service
case $SERVICE_MODE in
    "timer")
        print_info "Enabling and starting timer..."
        systemctl enable markdown-transcription.timer
        systemctl start markdown-transcription.timer
        
        echo ""
        print_info "✅ Timer service setup complete!"
        print_info "Status: $(systemctl is-active markdown-transcription.timer)"
        print_info "Next run: $(systemctl list-timers markdown-transcription.timer --no-pager | tail -n 1 | awk '{print $1, $2}')"
        ;;
    "path")
        print_info "Enabling and starting path monitor..."
        systemctl enable markdown-transcription.path
        systemctl start markdown-transcription.path
        
        echo ""
        print_info "✅ Path monitor service setup complete!"
        print_info "Status: $(systemctl is-active markdown-transcription.path)"
        print_info "Monitoring: $VAULT_PATH"
        ;;
    "oneshot")
        print_info "Enabling service..."
        systemctl enable markdown-transcription.service
        
        echo ""
        print_info "✅ One-shot service setup complete!"
        print_info "Run manually with: sudo systemctl start markdown-transcription.service"
        ;;
esac

# Show status
echo ""
echo "Service Management Commands:"
echo "============================"
case $SERVICE_MODE in
    "timer")
        echo "Check status:    sudo systemctl status markdown-transcription.timer"
        echo "View logs:       sudo journalctl -u markdown-transcription.service -f"
        echo "Stop timer:      sudo systemctl stop markdown-transcription.timer"
        echo "Disable timer:   sudo systemctl disable markdown-transcription.timer"
        echo "List timers:     systemctl list-timers markdown-transcription.timer"
        ;;
    "path")
        echo "Check status:    sudo systemctl status markdown-transcription.path"
        echo "View logs:       sudo journalctl -u markdown-transcription.service -f"
        echo "Stop monitor:    sudo systemctl stop markdown-transcription.path"
        echo "Disable monitor: sudo systemctl disable markdown-transcription.path"
        ;;
    "oneshot")
        echo "Run service:     sudo systemctl start markdown-transcription.service"
        echo "Check status:    sudo systemctl status markdown-transcription.service"
        echo "View logs:       sudo journalctl -u markdown-transcription.service -f"
        echo "Disable service: sudo systemctl disable markdown-transcription.service"
        ;;
esac

echo ""
echo "Configuration file: $CONFIG_FILE"
echo "Service file: $SERVICE_FILE"

if [[ "$SERVICE_MODE" == "timer" ]]; then
    echo "Timer file: $TIMER_FILE"
elif [[ "$SERVICE_MODE" == "path" ]]; then
    echo "Path file: $PATH_FILE"
fi

echo ""
print_info "Setup complete! The service is now configured and running."
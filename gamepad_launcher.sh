#!/bin/bash

# USB Gamepad Auto-Launcher for Mac
# This script monitors for USB gamepad connections and automatically starts the mapper

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/gamepad_mapper.py"
LOG_FILE="$SCRIPT_DIR/gamepad_mapper.log"

# Function to check if gamepad is connected
check_gamepad() {
    # Check for USB gamepad devices
    if system_profiler SPUSBDataType | grep -i "gamepad\|controller" > /dev/null 2>&1; then
        return 0
    fi
    
    # Alternative check using IOKit
    if ioreg -p IOUSB -l | grep -i "gamepad\|controller" > /dev/null 2>&1; then
        return 0
    fi
    
    return 1
}

# Function to start the gamepad mapper
start_mapper() {
    echo "$(date): Starting gamepad mapper..." >> "$LOG_FILE"
    
    # Check if Python script exists
    if [ ! -f "$PYTHON_SCRIPT" ]; then
        echo "$(date): Error: Python script not found at $PYTHON_SCRIPT" >> "$LOG_FILE"
        return 1
    fi
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        echo "$(date): Error: Python3 not found" >> "$LOG_FILE"
        return 1
    fi
    
    # Install dependencies if needed
    if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
        echo "$(date): Installing dependencies..." >> "$LOG_FILE"
        pip3 install -r "$SCRIPT_DIR/requirements.txt" >> "$LOG_FILE" 2>&1
    fi
    
    # Make script executable
    chmod +x "$PYTHON_SCRIPT"
    
    # Start the mapper
    echo "$(date): Launching gamepad mapper..." >> "$LOG_FILE"
    python3 "$PYTHON_SCRIPT" >> "$LOG_FILE" 2>&1 &
    MAPPER_PID=$!
    echo "$MAPPER_PID" > "$SCRIPT_DIR/mapper.pid"
    
    echo "$(date): Gamepad mapper started with PID $MAPPER_PID" >> "$LOG_FILE"
}

# Function to stop the gamepad mapper
stop_mapper() {
    if [ -f "$SCRIPT_DIR/mapper.pid" ]; then
        PID=$(cat "$SCRIPT_DIR/mapper.pid")
        if kill -0 "$PID" 2>/dev/null; then
            echo "$(date): Stopping gamepad mapper (PID: $PID)..." >> "$LOG_FILE"
            kill "$PID"
            rm -f "$SCRIPT_DIR/mapper.pid"
        fi
    fi
}

# Function to cleanup on exit
cleanup() {
    echo "$(date): Launcher shutting down..." >> "$LOG_FILE"
    stop_mapper
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo "$(date): USB Gamepad Auto-Launcher started" >> "$LOG_FILE"

# Main monitoring loop
while true; do
    if check_gamepad; then
        # Gamepad detected
        if [ ! -f "$SCRIPT_DIR/mapper.pid" ] || ! kill -0 "$(cat "$SCRIPT_DIR/mapper.pid")" 2>/dev/null; then
            echo "$(date): Gamepad detected, starting mapper..." >> "$LOG_FILE"
            start_mapper
        fi
    else
        # No gamepad detected
        if [ -f "$SCRIPT_DIR/mapper.pid" ] && kill -0 "$(cat "$SCRIPT_DIR/mapper.pid")" 2>/dev/null; then
            echo "$(date): Gamepad disconnected, stopping mapper..." >> "$LOG_FILE"
            stop_mapper
        fi
    fi
    
    # Wait before checking again
    sleep 2
done 
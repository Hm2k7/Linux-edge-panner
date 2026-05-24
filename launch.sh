#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Step 1: Install if this is the first run
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "First run detected — installing dependencies..."
    bash "$SCRIPT_DIR/install.sh"
    echo ""
    echo "NOTE: A reboot is recommended before first use so touchpad"
    echo "permissions take effect. If calibration fails, reboot and try again."
    echo ""
    read -p "Press Enter to continue or Ctrl+C to reboot now..."
fi

# Step 2: Calibrate if no config exists yet
if [ ! -f "$SCRIPT_DIR/config.json" ]; then
    echo "No calibration found. Launching calibration GUI..."
    "$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/panner_gui.py"
else
    # Step 3: Everything is set up — run the daemon
    echo "Calibration found. Starting Edge Panner..."
    "$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/edge_daemon.py"
fi

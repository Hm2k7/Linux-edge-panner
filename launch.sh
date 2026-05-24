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
    # Step 3: Config exists — show a menu
    echo ""
    echo "  ┌─────────────────────────────┐"
    echo "  │        Edge Panner          │"
    echo "  ├─────────────────────────────┤"
    echo "  │  1. Start panning           │"
    echo "  │  2. Open settings / recal.  │"
    echo "  │  3. Exit                    │"
    echo "  └─────────────────────────────┘"
    echo ""
    read -p "  Choose [1/2/3]: " choice

    case $choice in
        2) "$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/panner_gui.py" ;;
        3) exit 0 ;;
        *) echo "Starting Edge Panner..."
           "$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/edge_daemon.py" ;;
    esac
fi

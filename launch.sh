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

# Step 2: Always open the GUI — it starts the daemon on Save & Close
"$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/panner_gui.py"

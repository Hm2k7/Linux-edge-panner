#!/bin/bash

echo "======================================"
echo " Edge Panner Setup "
echo "======================================"

echo "[1/4] Installing system dependencies..."
sudo apt update
sudo apt install -y python3-evdev python3-tk python3-venv

echo "[2/4] Setting up hardware permissions..."
# Add user to the input group to read touchpad data without root
sudo usermod -aG input $USER

echo "[3/4] Creating Python Virtual Environment..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 -m venv "$SCRIPT_DIR/venv" --system-site-packages
"$SCRIPT_DIR/venv/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"

echo "[4/4] Creating desktop shortcut..."
chmod +x "$SCRIPT_DIR/launch.sh"
DESKTOP_FILE="$HOME/Desktop/EdgePanner.desktop"
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=Edge Panner
Comment=Touchpad edge panning — click to calibrate or start
Exec=bash -c "$SCRIPT_DIR/launch.sh; exec bash"
Terminal=true
Type=Application
Icon=$SCRIPT_DIR/.assets/.icon.png
Categories=Utility;
EOF
chmod +x "$DESKTOP_FILE"

# Trust the shortcut so Nemo/Nautilus allows double-click without a warning
gio set "$DESKTOP_FILE" metadata::trusted true 2>/dev/null || true

# Stamp the custom icon onto launch.sh so it shows in the file manager
gio set "$SCRIPT_DIR/launch.sh" metadata::custom-icon "file://$SCRIPT_DIR/.assets/.icon.png" 2>/dev/null || true

echo "======================================"
echo " INSTALLATION COMPLETE!"
echo "======================================"
echo "A shortcut 'Edge Panner' has been added to your Desktop."
echo "IMPORTANT: Reboot your computer now for hardware permissions to take effect."
echo "After rebooting, just double-click the Edge Panner icon on your Desktop."

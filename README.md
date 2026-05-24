# Linux Edge Panner

A lightweight, ultra-smooth background daemon that restores "Edge Motion" (edge panning) to modern Linux touchpads using `libinput`. If you've ever run out of trackpad space while dragging a file or drawing a screenshot box, this tool fixes it by letting the cursor glide seamlessly when your finger hits the hardware boundary.

## Installation

**One-liner install** — paste this into a terminal:

```bash
git clone https://github.com/Hm2k7/linux-edge-panner.git && cd linux-edge-panner && ./install.sh
```

Then **reboot** (required for touchpad hardware permissions to take effect).

After rebooting, an **Edge Panner** icon will be on your Desktop — just double-click it.

## Using Edge Panner

Double-clicking the Desktop icon always opens the GUI. From there:

1. Click **Start Calibration**
2. Swipe your finger to the extreme edges and corners of your touchpad
3. Click **Stop Recording** when done
4. Adjust the **Pan Speed** and **Edge Zone** sliders to your liking
5. Click **Save & Close** — the panner starts running immediately in the background

## Autostart on Boot

To make the panner start silently every time you log in:

1. Open your system's **Startup Applications** menu.
2. Add a new **Custom Command**.
3. Set the command to:
   ```
   /home/YOUR_USERNAME/linux-edge-panner/launch.sh
   ```
   Replace `YOUR_USERNAME` with your actual Linux username.

## How It Works

The daemon reads raw hardware events directly from the touchpad device (`/dev/input/`). When your finger position exceeds the calibrated edge threshold, it nudges the mouse cursor in that direction at a fixed speed — creating smooth, continuous panning without any desktop compositor involvement.

## Tuning

Open the GUI at any time by double-clicking the Desktop icon. Use the sliders to adjust:

| Setting | Description |
|---------|-------------|
| **Pan Speed** | How many pixels the cursor moves per tick (1 = slow, 10 = fast) |
| **Edge Zone** | How close to the edge your finger needs to be to trigger panning |

Changes take effect the next time you click **Save & Close**.

## Requirements

- Linux (tested on Linux Mint / Ubuntu)
- Python 3.8+
- A `libinput`-managed touchpad

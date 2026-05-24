# Linux Edge Panner

A lightweight, ultra-smooth background daemon that restores "Edge Motion" (edge panning) to modern Linux touchpads using `libinput`. If you've ever run out of trackpad space while dragging a file or drawing a screenshot box, this tool fixes it by letting the cursor glide seamlessly when your finger hits the hardware boundary.

## Installation

**One-liner install** — paste this into a terminal:

```bash
git clone https://github.com/Hm2k7/linux-edge-panner.git && cd linux-edge-panner && ./install.sh
```

Then **reboot** (required for touchpad hardware permissions to take effect).

After rebooting, an **Edge Panner** icon will be on your Desktop — just double-click it.

## First Launch (Calibration)

The first time you double-click the icon, the calibration GUI opens automatically:

1. Click **Start Calibration**
2. Swipe your finger to the extreme edges and corners of your touchpad
3. Click **Save Calibration**

After that, double-clicking the icon starts the panning daemon directly — no recalibration needed.

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

Edit `config.json` after calibration to adjust behaviour:

| Key | Default | Description |
|-----|---------|-------------|
| `edge_tolerance` | `150` | How close (in raw units) to the edge triggers panning |
| `pan_speed` | `4` | Pixels moved per tick (~5 ms) when panning |

## Requirements

- Linux (tested on Linux Mint / Ubuntu)
- Python 3.8+
- A `libinput`-managed touchpad

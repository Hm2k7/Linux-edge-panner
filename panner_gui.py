import tkinter as tk
from tkinter import messagebox
import threading
import json
import os
import evdev

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

# ── Palette ────────────────────────────────────────────────────────────────
BG         = "#0e0e10"
BG_CARD    = "#18181b"
BG_INPUT   = "#27272a"
BORDER     = "#3f3f46"
ACCENT     = "#6366f1"
ACCENT_DIM = "#4338ca"
TEXT       = "#f4f4f5"
TEXT_DIM   = "#a1a1aa"
TEXT_MUTED = "#52525b"
SUCCESS    = "#22c55e"
WARNING    = "#f59e0b"
ERROR      = "#ef4444"


class CalibrationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Edge Panner")
        self.root.geometry("560x600")
        self.root.configure(bg=BG)
        self.root.resizable(False, True)

        self.device_path = self.find_touchpad()
        self.calibrating = False
        self.max_x, self.max_y = 0, 0
        self.live_x, self.live_y = 0, 0

        existing = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                existing = json.load(f)

        self.pan_speed_var      = tk.IntVar(value=existing.get("pan_speed", 2))
        self.edge_tolerance_var = tk.IntVar(value=existing.get("edge_tolerance", 150))

        self._build_scroll_shell()
        self.setup_ui()

    # ── Device detection ───────────────────────────────────────────────────
    def find_touchpad(self):
        for path in evdev.list_devices():
            name = evdev.InputDevice(path).name.lower()
            if any(k in name for k in ("touchpad", "synaptics", "elan", "alps")):
                return path
        return None

    # ── Scrollable shell ───────────────────────────────────────────────────
    def _build_scroll_shell(self):
        self._scroll_canvas = tk.Canvas(self.root, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical",
                                 command=self._scroll_canvas.yview)
        self._scroll_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self._scroll_canvas.pack(side="left", fill="both", expand=True)

        self.frame = tk.Frame(self._scroll_canvas, bg=BG)
        self._win_id = self._scroll_canvas.create_window(
            (0, 0), window=self.frame, anchor="nw"
        )

        self.frame.bind("<Configure>", self._on_frame_resize)
        self._scroll_canvas.bind("<Configure>", self._on_canvas_resize)

        # mousewheel — Linux uses Button-4/5
        for widget in (self._scroll_canvas, self.root):
            widget.bind("<Button-4>", lambda e: self._scroll_canvas.yview_scroll(-1, "units"))
            widget.bind("<Button-5>", lambda e: self._scroll_canvas.yview_scroll( 1, "units"))

    def _on_frame_resize(self, event):
        self._scroll_canvas.configure(scrollregion=self._scroll_canvas.bbox("all"))

    def _on_canvas_resize(self, event):
        self._scroll_canvas.itemconfig(self._win_id, width=event.width)

    # ── Layout helpers ─────────────────────────────────────────────────────
    def card(self, pady=(0, 10)):
        f = tk.Frame(self.frame, bg=BG_CARD, padx=20, pady=16,
                     highlightbackground=BORDER, highlightthickness=1)
        f.pack(fill="x", padx=24, pady=pady)
        return f

    def section_label(self, parent, text):
        tk.Label(parent, text=text, fg=TEXT_MUTED, bg=BG_CARD,
                 font=("monospace", 8, "bold")).pack(anchor="w", pady=(0, 10))

    def divider(self, parent):
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", pady=8)

    # ── Main UI ────────────────────────────────────────────────────────────
    def setup_ui(self):
        self._build_header()
        self._build_device_card()
        if not self.device_path:
            return
        self._build_calibration_card()
        self._build_settings_card()
        self._build_save_button()

    def _build_header(self):
        h = tk.Frame(self.frame, bg=BG, pady=22)
        h.pack(fill="x")
        tk.Label(h, text="Edge Panner", font=("sans-serif", 22, "bold"),
                 bg=BG, fg=TEXT).pack()
        tk.Label(h, text="Calibrate your touchpad edges",
                 font=("sans-serif", 10), bg=BG, fg=TEXT_MUTED).pack(pady=(3, 0))

    def _build_device_card(self):
        c = self.card(pady=(0, 10))
        row = tk.Frame(c, bg=BG_CARD)
        row.pack(fill="x")
        if self.device_path:
            tk.Label(row, text="●", fg=SUCCESS, bg=BG_CARD,
                     font=("Arial", 13)).pack(side="left", padx=(0, 8))
            tk.Label(row, text="Touchpad detected", fg=TEXT,
                     bg=BG_CARD, font=("sans-serif", 11, "bold")).pack(side="left")
            tk.Label(c, text=self.device_path, fg=TEXT_MUTED,
                     bg=BG_CARD, font=("monospace", 9)).pack(anchor="w", pady=(5, 0))
        else:
            tk.Label(row, text="●", fg=ERROR, bg=BG_CARD,
                     font=("Arial", 13)).pack(side="left", padx=(0, 8))
            tk.Label(row, text="No touchpad found — try rebooting",
                     fg=ERROR, bg=BG_CARD, font=("sans-serif", 11)).pack(side="left")

    def _build_calibration_card(self):
        c = self.card()
        self.section_label(c, "CALIBRATION")

        CW, CH = 460, 200
        self.canvas = tk.Canvas(c, width=CW, height=CH,
                                bg=BG_INPUT, highlightbackground=BORDER,
                                highlightthickness=1, cursor="crosshair")
        self.canvas.pack(pady=(0, 14))
        self._cw, self._ch = CW, CH

        s = 16
        for x1, y1, x2, y2, x3, y3 in [
            (0, s, 0, 0, s, 0),
            (CW-s, 0, CW, 0, CW, s),
            (0, CH-s, 0, CH, s, CH),
            (CW-s, CH, CW, CH, CW, CH-s),
        ]:
            self.canvas.create_line(x1, y1, x2, y2, x3, y3, fill=BORDER, width=1)

        self.canvas.create_text(CW//2, CH//2,
                                text="press Start, then swipe to every edge",
                                fill=TEXT_MUTED, font=("sans-serif", 10), tags="hint")
        self.dot = self.canvas.create_oval(0, 0, 0, 0, fill=ACCENT, outline="")

        self.instruction_var = tk.StringVar()
        if os.path.exists(CONFIG_FILE):
            self.instruction_var.set("Config found. Click Save or recalibrate to remap edges.")
        else:
            self.instruction_var.set("Press Start, then swipe to every corner and edge.")

        tk.Label(c, textvariable=self.instruction_var,
                 fg=TEXT_DIM, bg=BG_CARD, font=("sans-serif", 10),
                 justify="center", wraplength=460).pack(pady=(0, 12))

        btn_row = tk.Frame(c, bg=BG_CARD)
        btn_row.pack(fill="x")

        self.btn_start = tk.Button(
            btn_row, text="Start Calibration", command=self.start_reading,
            bg=ACCENT, fg=TEXT, activebackground=ACCENT_DIM, activeforeground=TEXT,
            font=("sans-serif", 10, "bold"), relief="flat", cursor="hand2",
            padx=14, pady=7, bd=0
        )
        self.btn_start.pack(side="left")

        self.status_dot  = tk.Label(btn_row, text="", bg=BG_CARD, font=("Arial", 11))
        self.status_text = tk.Label(btn_row, text="", fg=TEXT_MUTED, bg=BG_CARD,
                                    font=("monospace", 9))
        self.status_dot.pack(side="left", padx=(12, 4))
        self.status_text.pack(side="left")

        # forward mousewheel on the calibration canvas to the scroll container
        self.canvas.bind("<Button-4>", lambda e: self._scroll_canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Button-5>", lambda e: self._scroll_canvas.yview_scroll( 1, "units"))

    def _build_settings_card(self):
        c = self.card()
        self.section_label(c, "SETTINGS")
        self._slider_row(c, "Pan Speed", self.pan_speed_var, 1, 10,
                         "Pixels moved per tick  (1 = slow, 10 = fast)")
        self.divider(c)
        self._slider_row(c, "Edge Zone", self.edge_tolerance_var, 50, 400,
                         "Width of the trigger zone  (higher = triggers sooner)")

    def _slider_row(self, parent, label, variable, lo, hi, hint):
        row = tk.Frame(parent, bg=BG_CARD)
        row.pack(fill="x", pady=(0, 6))

        header = tk.Frame(row, bg=BG_CARD)
        header.pack(fill="x")
        tk.Label(header, text=label, fg=TEXT, bg=BG_CARD,
                 font=("sans-serif", 11, "bold")).pack(side="left")
        tk.Label(header, text=hint, fg=TEXT_MUTED, bg=BG_CARD,
                 font=("sans-serif", 9)).pack(side="left", padx=(10, 0))

        tk.Scale(row, from_=lo, to=hi, orient="horizontal", variable=variable,
                 bg=BG_CARD, fg=TEXT, troughcolor=BG_INPUT,
                 activebackground=ACCENT, highlightthickness=0,
                 sliderrelief="flat", showvalue=True,
                 font=("monospace", 9)).pack(fill="x")

    def _build_save_button(self):
        f = tk.Frame(self.frame, bg=BG)
        f.pack(fill="x", padx=24, pady=(4, 28))

        self.btn_save = tk.Button(
            f, text="Save & Close", command=self.save_config,
            state=tk.NORMAL if os.path.exists(CONFIG_FILE) else tk.DISABLED,
            bg=SUCCESS, fg="#0e0e10",
            activebackground="#16a34a", activeforeground="#0e0e10",
            font=("sans-serif", 12, "bold"), relief="flat", cursor="hand2",
            pady=11, bd=0
        )
        self.btn_save.pack(fill="x")

    # ── Calibration logic ──────────────────────────────────────────────────
    def start_reading(self):
        if self.calibrating:
            self.calibrating = False
            self.btn_start.config(text="Start Calibration", bg=ACCENT, fg=TEXT,
                                  activebackground=ACCENT_DIM)
            self.status_dot.config(text="●", fg=SUCCESS)
            self.status_text.config(text="stopped — click Save & Close when ready")
            return

        self.calibrating = True
        self.max_x, self.max_y = 0, 0
        self.btn_start.config(text="Stop Recording", bg="#b91c1c", fg=TEXT,
                              activebackground="#991b1b")
        self.btn_save.config(state=tk.NORMAL)
        self.instruction_var.set("Recording... swipe slowly to every corner and edge.")
        self.status_dot.config(text="●", fg=WARNING)
        self.status_text.config(text="recording")
        self.canvas.delete("hint")
        threading.Thread(target=self.read_hardware, daemon=True).start()

    def read_hardware(self):
        try:
            device = evdev.InputDevice(self.device_path)
            for event in device.read_loop():
                if not self.calibrating:
                    break
                if event.type == evdev.ecodes.EV_ABS:
                    if event.code == evdev.ecodes.ABS_X:
                        self.live_x = event.value
                        if event.value > self.max_x:
                            self.max_x = event.value
                    elif event.code == evdev.ecodes.ABS_Y:
                        self.live_y = event.value
                        if event.value > self.max_y:
                            self.max_y = event.value
                    self.root.after(0, self._update_canvas)
        except PermissionError:
            messagebox.showerror("Permission Error",
                "Please reboot so the 'input' group permissions take effect.")

    def _update_canvas(self):
        if self.max_x == 0 or self.max_y == 0:
            return
        r = 6
        cx = max(r, min(self._cw - r, int(self.live_x / self.max_x * self._cw)))
        cy = max(r, min(self._ch - r, int(self.live_y / self.max_y * self._ch)))
        self.canvas.coords(self.dot, cx-r, cy-r, cx+r, cy+r)
        self.status_text.config(
            text=f"x={self.live_x}  y={self.live_y}  |  max {self.max_x}×{self.max_y}"
        )

    # ── Save ───────────────────────────────────────────────────────────────
    def save_config(self):
        self.calibrating = False

        x_max, y_max = self.max_x, self.max_y
        if x_max == 0 and os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                old = json.load(f)
            x_max = old.get("x_max", 0)
            y_max = old.get("y_max", 0)

        with open(CONFIG_FILE, "w") as f:
            json.dump({
                "device_path":    self.device_path,
                "x_max":          x_max,
                "y_max":          y_max,
                "edge_tolerance": self.edge_tolerance_var.get(),
                "pan_speed":      self.pan_speed_var.get()
            }, f, indent=4)

        script_dir  = os.path.dirname(os.path.abspath(__file__))
        python_path = os.path.join(script_dir, "venv", "bin", "python")
        daemon_path = os.path.join(script_dir, "edge_daemon.py")
        messagebox.showinfo("Saved", (
            "Calibration saved!\n\n"
            "To autostart on login:\n"
            "1. Open Startup Applications\n"
            "2. Add a Custom Command:\n"
            f"   {python_path} {daemon_path}"
        ))
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = CalibrationApp(root)
    root.mainloop()

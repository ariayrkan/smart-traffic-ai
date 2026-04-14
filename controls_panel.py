import tkinter as tk
from tkinter import ttk
from theme import (
    PANEL, PANEL_ALT, CARD, CARD_ALT, BORDER,
    TEXT, MUTED, DIMMED,
    ACCENT, SUCCESS, WARNING, DANGER, ORANGE,
    FONT, FONT_TEXT
)


class ControlsPanel:
    def __init__(self, parent, on_speed_change, on_pause_toggle, on_scenario_change):
        self.frame = tk.Frame(parent, bg=PANEL)
        self.on_speed_change    = on_speed_change
        self.on_pause_toggle    = on_pause_toggle
        self.on_scenario_change = on_scenario_change
        self.paused             = False

        # Header
        header = tk.Frame(self.frame, bg=PANEL)
        header.pack(fill="x", padx=20, pady=(18, 0))

        tk.Label(
            header, text="Controls",
            bg=PANEL, fg=TEXT,
            font=(FONT, 22, "bold")
        ).pack(side="left")

        tk.Frame(self.frame, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(12, 0))

        # ── Playback speed ───────────────────────────────────
        spd_wrap = tk.Frame(self.frame, bg=PANEL)
        spd_wrap.pack(fill="x", padx=20, pady=(14, 0))

        tk.Label(
            spd_wrap, text="PLAYBACK SPEED",
            bg=PANEL, fg=MUTED,
            font=(FONT_TEXT, 9)
        ).pack(anchor="w")

        spd_row = tk.Frame(spd_wrap, bg=PANEL)
        spd_row.pack(fill="x", pady=(8, 0))

        self.speed_btns = {}
        for label, ms in [("0.5×", 2000), ("1×", 1000), ("2×", 500), ("4×", 250)]:
            btn = tk.Button(
                spd_row, text=label,
                bg=CARD if label != "1×" else ACCENT,
                fg=TEXT if label != "1×" else "#000000",
                relief="flat",
                font=(FONT_TEXT, 11, "bold"),
                padx=0, pady=8, width=5,
                command=lambda l=label, m=ms: self._set_speed(l, m)
            )
            btn.pack(side="left", padx=(0, 8))
            self.speed_btns[label] = btn

        # ── Pause / Resume ───────────────────────────────────
        tk.Frame(self.frame, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(14, 0))

        self.pause_btn = tk.Button(
            self.frame,
            text="Pause Stream",
            bg=CARD, fg=TEXT,
            relief="flat",
            font=(FONT_TEXT, 12, "bold"),
            pady=10,
            command=self._toggle_pause
        )
        self.pause_btn.pack(fill="x", padx=20, pady=(12, 0))

        # ── Scenario selector ────────────────────────────────
        tk.Frame(self.frame, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(14, 0))

        tk.Label(
            self.frame, text="SCENARIO",
            bg=PANEL, fg=MUTED,
            font=(FONT_TEXT, 9)
        ).pack(anchor="w", padx=20, pady=(12, 6))

        scenarios = [
            ("Normal Traffic",  "normal",   SUCCESS, "#0D2B17"),
            ("Sensor Spoofing", "spoofing", DANGER,  "#2B0D0B"),
            ("Heavy Traffic",   "heavy",    WARNING, "#2B2200"),
            ("Recovery Mode",   "recovery", ACCENT,  "#001833"),
        ]

        scen_grid = tk.Frame(self.frame, bg=PANEL)
        scen_grid.pack(fill="x", padx=20, pady=(0, 14))

        for i, (label, key, fg, bg) in enumerate(scenarios):
            row, col = divmod(i, 2)
            btn = tk.Button(
                scen_grid,
                text=label,
                bg=bg, fg=fg,
                relief="flat",
                font=(FONT_TEXT, 11, "bold"),
                pady=12,
                command=lambda k=key, l=label: self._set_scenario(k, l)
            )
            btn.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            scen_grid.grid_columnconfigure(col, weight=1)

        # ── Status bar ───────────────────────────────────────
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(
            self.frame,
            textvariable=self.status_var,
            bg=PANEL_ALT, fg=MUTED,
            font=(FONT_TEXT, 10),
            pady=8, padx=16,
            anchor="w"
        ).pack(fill="x", padx=20, pady=(0, 16))

    # ── Internal helpers ─────────────────────────────────────
    def _set_speed(self, label, ms):
        for lbl, btn in self.speed_btns.items():
            if lbl == label:
                btn.config(bg=ACCENT, fg="#000000")
            else:
                btn.config(bg=CARD, fg=TEXT)
        self.on_speed_change(ms)
        self.status_var.set(f"Speed set to {label}")

    def _toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.pause_btn.config(text="Resume Stream", bg=ACCENT, fg="#000000")
            self.status_var.set("Stream paused")
        else:
            self.pause_btn.config(text="Pause Stream", bg=CARD, fg=TEXT)
            self.status_var.set("Stream resumed")
        self.on_pause_toggle(self.paused)

    def _set_scenario(self, key, label):
        self.on_scenario_change(key)
        self.status_var.set(f"Scenario → {label}")

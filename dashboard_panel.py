import tkinter as tk
from theme import (
    PANEL, PANEL_ALT, CARD, CARD_ALT, BORDER, BORDER2,
    TEXT, TEXT2, MUTED, DIMMED,
    ACCENT, SUCCESS, WARNING, DANGER, ORANGE, TEAL,
    SUCCESS_DIM, WARNING_DIM, DANGER_DIM, ACCENT_DIM,
    FONT, FONT_TEXT
)


class DashboardPanel:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg=PANEL)
        self.cards = {}
        self.alert_flash = False
        self._flash_after = None

        # ── Section label ────────────────────────────────────
        header = tk.Frame(self.frame, bg=PANEL)
        header.pack(fill="x", padx=20, pady=(20, 0))

        tk.Label(
            header, text="Overview",
            bg=PANEL, fg=TEXT,
            font=(FONT, 22, "bold")
        ).pack(side="left")

        # Live status pill (top-right)
        self.status_pill = tk.Label(
            header,
            text="  ●  All Systems Normal  ",
            bg=SUCCESS_DIM, fg=SUCCESS,
            font=(FONT_TEXT, 10, "bold"),
            padx=0, pady=4
        )
        self.status_pill.pack(side="right")

        # Subtle divider
        tk.Frame(self.frame, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(12, 0))

        # ── Metric cards grid ────────────────────────────────
        grid = tk.Frame(self.frame, bg=PANEL)
        grid.pack(fill="x", padx=16, pady=(14, 0))

        self._metric(grid, "Step",         "—",          0, 0)
        self._metric(grid, "Mode",         "—",          0, 1)
        self._metric(grid, "Real Count",   "—",          1, 0)
        self._metric(grid, "Sensor Count", "—",          1, 1)
        self._metric(grid, "Avg Speed",    "—",          2, 0)
        self._metric(grid, "Waiting",      "—",          2, 1)

        # ── Risk indicator row ────────────────────────────────
        risk_row = tk.Frame(self.frame, bg=PANEL)
        risk_row.pack(fill="x", padx=16, pady=(10, 0))

        self.risk_vars = {}
        self.risk_colors = {}
        self.risk_labels = {}

        for col, (label, val, color) in enumerate([
            ("Risk Level",   "LOW",     SUCCESS),
            ("Sensor Trust", "HIGH",    ACCENT),
            ("Failover",     "STANDBY", WARNING),
        ]):
            self._risk_chip(risk_row, label, val, color, col)

        # ── Intersection map ─────────────────────────────────
        map_wrap = tk.Frame(self.frame, bg=PANEL_ALT)
        map_wrap.pack(fill="both", expand=True, padx=16, pady=(12, 16))

        map_header = tk.Frame(map_wrap, bg=PANEL_ALT)
        map_header.pack(fill="x", padx=14, pady=(10, 0))

        tk.Label(
            map_header, text="Intersection",
            bg=PANEL_ALT, fg=MUTED,
            font=(FONT_TEXT, 11)
        ).pack(side="left")

        self.light_label = tk.Label(
            map_header, text="● Green",
            bg=PANEL_ALT, fg=SUCCESS,
            font=(FONT_TEXT, 11, "bold")
        )
        self.light_label.pack(side="right")

        self.map_canvas = tk.Canvas(
            map_wrap, bg=PANEL_ALT, height=160,
            highlightthickness=0
        )
        self.map_canvas.pack(fill="x", padx=14, pady=(6, 12))

        self.real_text   = None
        self.sensor_text = None
        self.light_dot   = None
        self._draw_map_base()

    # ── Metric card ──────────────────────────────────────────
    def _metric(self, parent, label, default, row, col):
        card = tk.Frame(parent, bg=PANEL_ALT, padx=16, pady=14)
        card.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
        parent.grid_columnconfigure(col, weight=1)

        tk.Label(
            card, text=label.upper(),
            bg=PANEL_ALT, fg=MUTED,
            font=(FONT_TEXT, 9)
        ).pack(anchor="w")

        var = tk.StringVar(value=default)
        tk.Label(
            card, textvariable=var,
            bg=PANEL_ALT, fg=TEXT,
            font=(FONT, 20, "bold")
        ).pack(anchor="w", pady=(2, 0))

        self.cards[label] = var

    # ── Risk chip ────────────────────────────────────────────
    def _risk_chip(self, parent, label, val, color, col):
        chip = tk.Frame(parent, bg=CARD, padx=14, pady=10)
        chip.grid(row=0, column=col, sticky="nsew", padx=5)
        parent.grid_columnconfigure(col, weight=1)

        tk.Label(
            chip, text=label.upper(),
            bg=CARD, fg=MUTED,
            font=(FONT_TEXT, 9)
        ).pack(anchor="w")

        var = tk.StringVar(value=val)
        lbl = tk.Label(
            chip, textvariable=var,
            bg=CARD, fg=color,
            font=(FONT_TEXT, 13, "bold")
        )
        lbl.pack(anchor="w", pady=(2, 0))

        self.risk_vars[label]   = var
        self.risk_labels[label] = lbl
        self.risk_colors[label] = color

    def _set_risk(self, label, val, color):
        self.risk_vars[label].set(val)
        self.risk_labels[label].config(fg=color)

    # ── Intersection map drawing ──────────────────────────────
    def _draw_map_base(self):
        c = self.map_canvas
        c.delete("all")
        W, H = 620, 160

        # Road surface
        c.create_rectangle(0, H*0.32, W, H*0.68, fill="#1C1C1E", outline="")
        c.create_rectangle(W*0.42, 0, W*0.58, H,  fill="#1C1C1E", outline="")

        # Lane markings — subtle dashed
        c.create_line(0, H/2, W, H/2, fill="#3A3A3C", dash=(10, 8), width=1)
        c.create_line(W/2, 0, W/2, H,  fill="#3A3A3C", dash=(10, 8), width=1)

        # Intersection circle
        cx, cy, r = W/2, H/2, 22
        c.create_oval(cx-r, cy-r, cx+r, cy+r, fill="#2C2C2E", outline="#48484A", width=1)
        self.light_dot = c.create_oval(
            cx-10, cy-10, cx+10, cy+10,
            fill=SUCCESS, outline=""
        )

        # Count labels
        self.real_text   = c.create_text(60,  20, text="Real: —",   fill=SUCCESS, font=(FONT_TEXT, 11, "bold"), anchor="w")
        self.sensor_text = c.create_text(W-60, 20, text="Sensor: —", fill=TEAL,    font=(FONT_TEXT, 11, "bold"), anchor="e")

    # ── Public update ──────────────────────────────────────────
    def update(self, snap):
        self.cards["Step"].set(str(snap.step))
        self.cards["Mode"].set(snap.mode)
        self.cards["Real Count"].set(str(snap.real_count))
        self.cards["Sensor Count"].set(str(snap.sensor_count))
        self.cards["Avg Speed"].set(f"{snap.avg_speed:.1f}")
        self.cards["Waiting"].set(f"{snap.waiting_time:.2f}s")

        gap = abs(snap.real_count - snap.sensor_count)

        if snap.attack_detected:
            # Flash between two red tones
            self.alert_flash = not self.alert_flash
            flash_fg = "#FF6961" if self.alert_flash else DANGER
            self.status_pill.config(
                text="  ⚠  Attack Detected — Failsafe Active  ",
                bg=DANGER_DIM, fg=flash_fg
            )
            self._set_risk("Risk Level",   "HIGH",    DANGER)
            self._set_risk("Sensor Trust", "LOW",     DANGER)
            self._set_risk("Failover",     "ACTIVE",  ORANGE)
            self.map_canvas.itemconfig(self.light_dot, fill=DANGER)
            self.light_label.config(text="● Red — Failsafe", fg=DANGER)

        elif gap > 7:
            self.status_pill.config(
                text="  ◐  Anomaly Watch — Validating Sensors  ",
                bg=WARNING_DIM, fg=WARNING
            )
            self._set_risk("Risk Level",   "MEDIUM",   WARNING)
            self._set_risk("Sensor Trust", "DEGRADED", WARNING)
            self._set_risk("Failover",     "READY",    ORANGE)
            self.map_canvas.itemconfig(self.light_dot, fill=WARNING)
            self.light_label.config(text="● Yellow — Caution", fg=WARNING)

        else:
            self.status_pill.config(
                text="  ●  All Systems Normal  ",
                bg=SUCCESS_DIM, fg=SUCCESS
            )
            self._set_risk("Risk Level",   "LOW",     SUCCESS)
            self._set_risk("Sensor Trust", "HIGH",    ACCENT)
            self._set_risk("Failover",     "STANDBY", MUTED)
            self.map_canvas.itemconfig(self.light_dot, fill=SUCCESS)
            self.light_label.config(text="● Green — Normal", fg=SUCCESS)

        self.map_canvas.itemconfig(self.real_text,   text=f"Real: {snap.real_count}")
        self.map_canvas.itemconfig(self.sensor_text, text=f"Sensor: {snap.sensor_count}")

import tkinter as tk
from theme import (
    PANEL, PANEL_ALT, CARD, BORDER,
    TEXT, MUTED, DIMMED,
    ACCENT, SUCCESS, WARNING, DANGER, TEAL,
    FONT, FONT_TEXT, MONO
)


class AnalyticsPanel:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg=PANEL)

        # Header row
        header = tk.Frame(self.frame, bg=PANEL)
        header.pack(fill="x", padx=20, pady=(18, 0))

        tk.Label(
            header, text="Live Analytics",
            bg=PANEL, fg=TEXT,
            font=(FONT, 22, "bold")
        ).pack(side="left")

        # Legend pills
        legend = tk.Frame(header, bg=PANEL)
        legend.pack(side="right")
        tk.Label(legend, text="●", bg=PANEL, fg=SUCCESS, font=(FONT_TEXT, 12)).pack(side="left")
        tk.Label(legend, text=" Real Count  ", bg=PANEL, fg=MUTED, font=(FONT_TEXT, 10)).pack(side="left")
        tk.Label(legend, text="●", bg=PANEL, fg=TEAL, font=(FONT_TEXT, 12)).pack(side="left")
        tk.Label(legend, text=" Sensor Count", bg=PANEL, fg=MUTED, font=(FONT_TEXT, 10)).pack(side="left")

        tk.Frame(self.frame, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(12, 0))

        # Chart canvas
        self.canvas = tk.Canvas(
            self.frame, bg=PANEL_ALT,
            height=220, highlightthickness=0
        )
        self.canvas.pack(fill="x", padx=16, pady=(12, 0))

        # Stat cards
        stat_row = tk.Frame(self.frame, bg=PANEL)
        stat_row.pack(fill="x", padx=16, pady=(10, 18))

        self.attack_var = tk.StringVar(value="0.0%")
        self.wait_var   = tk.StringVar(value="0.00s")
        self.gap_var    = tk.StringVar(value="0.00")

        self._stat(stat_row, "Attack Rate", self.attack_var, DANGER,  0)
        self._stat(stat_row, "Avg Wait",    self.wait_var,   WARNING, 1)
        self._stat(stat_row, "Avg Gap",     self.gap_var,    ACCENT,  2)

    def _stat(self, parent, label, var, color, col):
        card = tk.Frame(parent, bg=PANEL_ALT, padx=16, pady=12)
        card.grid(row=0, column=col, sticky="nsew", padx=5)
        parent.grid_columnconfigure(col, weight=1)

        tk.Label(
            card, text=label.upper(),
            bg=PANEL_ALT, fg=MUTED,
            font=(FONT_TEXT, 9)
        ).pack(anchor="w")

        tk.Label(
            card, textvariable=var,
            bg=PANEL_ALT, fg=color,
            font=(FONT, 20, "bold")
        ).pack(anchor="w", pady=(2, 0))

    def update(self, history, summary):
        self.attack_var.set(f"{summary['attack_rate'] * 100:.1f}%")
        self.wait_var.set(f"{summary['avg_wait']:.2f}s")
        self.gap_var.set(f"{summary['avg_gap']:.2f}")
        self._draw_graph(history)

    def _draw_graph(self, history):
        c = self.canvas
        c.delete("all")
        W = c.winfo_width()  or 900
        H = c.winfo_height() or 220
        PX, PY = 48, 24        # padding x, y

        # Background
        c.create_rectangle(0, 0, W, H, fill=PANEL_ALT, outline="")

        if len(history) < 2:
            c.create_text(
                W // 2, H // 2,
                text="Awaiting data…",
                fill=DIMMED, font=(FONT_TEXT, 12)
            )
            return

        max_y = max(max(i.real_count, i.sensor_count) for i in history) + 4
        max_y = max(max_y, 10)

        # Grid lines — very subtle
        grid_steps = 4
        for gi in range(grid_steps + 1):
            gy = PY + (H - 2 * PY) * gi / grid_steps
            gv = max_y * (1 - gi / grid_steps)
            c.create_line(PX, gy, W - PX/2, gy, fill="#2C2C2E", width=1)
            c.create_text(
                PX - 6, gy,
                text=str(int(gv)),
                fill=DIMMED, font=(MONO, 8),
                anchor="e"
            )

        # Helper: map values → canvas coords
        def pts(values):
            n   = len(values)
            spx = W - PX - PX / 2
            spy = H - 2 * PY
            result = []
            for idx, v in enumerate(values):
                x = PX + (idx / (n - 1)) * spx
                y = PY + spy * (1 - v / max_y)
                result.extend([x, y])
            return result

        real_pts   = pts([i.real_count   for i in history])
        sensor_pts = pts([i.sensor_count for i in history])

        # Filled area under real count — very subtle
        area_pts = list(real_pts)
        area_pts += [W - PX / 2, H - PY, PX, H - PY]
        c.create_polygon(*area_pts, fill="#0D2B17", outline="")

        # Lines
        c.create_line(*real_pts,   fill=SUCCESS, width=2, smooth=True)
        c.create_line(*sensor_pts, fill=TEAL,    width=2, smooth=True, dash=(6, 4))

        # Endpoint dots
        def dot(pts_list, color):
            lx, ly = pts_list[-2], pts_list[-1]
            c.create_oval(lx - 4, ly - 4, lx + 4, ly + 4, fill=color, outline=PANEL_ALT, width=2)

        dot(real_pts,   SUCCESS)
        dot(sensor_pts, TEAL)

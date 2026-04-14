import tkinter as tk
from datetime import datetime

from data_service import DataService, resolve_csv
from dashboard_panel import DashboardPanel
from analytics_panel import AnalyticsPanel
from controls_panel  import ControlsPanel
from events_panel    import EventsPanel
from theme import (
    BG, PANEL, PANEL_ALT, CARD, BORDER,
    TEXT, MUTED, DIMMED,
    ACCENT, SUCCESS, DANGER, WARNING,
    FONT, FONT_TEXT, MONO
)


class SmartTrafficDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Traffic AI  \u2022  Enterprise Dashboard")
        self.root.geometry("1600x960")
        self.root.configure(bg=BG)
        self.root.minsize(1400, 860)

        try:
            self.data_service = DataService(resolve_csv())
        except FileNotFoundError as e:
            self._show_startup_error(str(e))
            return

        self.running      = True
        self.tick_ms      = 1000
        self.autopilot    = False
        self._step        = 0
        self._total_steps = len(self.data_service.df)

        self._build_titlebar()
        self._build_scenario_bar()
        self._build_body()
        self._build_footer()
        self._bind_keys()
        self._tick()

    def _show_startup_error(self, msg):
        self.root.configure(bg=BG)
        frame = tk.Frame(self.root, bg=BG)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(frame, text="!", bg=BG, fg=DANGER,
                 font=(FONT, 56, "bold")).pack()
        tk.Label(frame, text="Could not load CSV data",
                 bg=BG, fg=TEXT, font=(FONT, 20, "bold")).pack(pady=(8, 4))
        tk.Label(frame, text=msg, bg=BG, fg=MUTED,
                 font=(FONT_TEXT, 11), wraplength=500).pack()
        tk.Label(frame,
                 text="Copy traffic_ai_attack_results (1).csv into the demo\\ folder and restart.",
                 bg=BG, fg=DIMMED, font=(FONT_TEXT, 10)).pack(pady=(12, 0))

    def _build_titlebar(self):
        bar = tk.Frame(self.root, bg=BG)
        bar.pack(fill="x", padx=24, pady=(18, 0))

        left = tk.Frame(bar, bg=BG)
        left.pack(side="left")

        logo_c = tk.Canvas(left, width=40, height=40, bg=BG, highlightthickness=0)
        logo_c.create_oval(1, 1, 39, 39, fill=ACCENT, outline="")
        logo_c.create_text(20, 20, text="AI", fill="#000000", font=(FONT, 11, "bold"))
        logo_c.pack(side="left", padx=(0, 12))

        titles = tk.Frame(left, bg=BG)
        titles.pack(side="left")
        tk.Label(titles, text="Smart Traffic AI",
                 bg=BG, fg=TEXT, font=(FONT, 26, "bold")).pack(anchor="w")
        tk.Label(titles,
                 text="Enterprise Control  \u2022  Live Telemetry  \u2022  Secure Monitoring",
                 bg=BG, fg=MUTED, font=(FONT_TEXT, 11)).pack(anchor="w", pady=(2, 0))

        right = tk.Frame(bar, bg=BG)
        right.pack(side="right")

        self.live_badge = tk.Label(
            right, text="\u25cf LIVE",
            bg=BG, fg=SUCCESS, font=(MONO, 11, "bold")
        )
        self.live_badge.pack(anchor="e")

        self.scenario_badge = tk.Label(
            right, text="NORMAL",
            bg=PANEL_ALT, fg=MUTED,
            font=(MONO, 9), padx=10, pady=4
        )
        self.scenario_badge.pack(anchor="e", pady=(6, 0))

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", padx=24, pady=(14, 0))

    def _build_scenario_bar(self):
        bar = tk.Frame(self.root, bg=PANEL_ALT)
        bar.pack(fill="x", padx=24, pady=(10, 0))

        tk.Label(bar, text="SCENARIO",
                 bg=PANEL_ALT, fg=DIMMED,
                 font=(MONO, 9), padx=12, pady=10).pack(side="left")

        tk.Frame(bar, bg=BORDER, width=1).pack(side="left", fill="y", pady=6)

        for label, scenario, fg in [
            ("Normal",   "normal",   SUCCESS),
            ("Spoofing", "spoofing", DANGER),
            ("Heavy",    "heavy",    WARNING),
            ("Recovery", "recovery", ACCENT),
        ]:
            tk.Button(
                bar, text=label,
                bg=PANEL_ALT, fg=fg,
                relief="flat",
                font=(FONT_TEXT, 10, "bold"),
                padx=18, pady=9,
                activebackground=CARD, activeforeground=fg,
                command=lambda s=scenario: self._set_scenario(s)
            ).pack(side="left")

        tk.Label(bar, text="[Space] Pause    [1-4] Speed    [N/S/H/R] Scenario    [Q] Quit",
                 bg=PANEL_ALT, fg=DIMMED,
                 font=(MONO, 8), padx=16).pack(side="left")

        self.auto_btn = tk.Button(
            bar, text="Auto Demo  OFF",
            bg=PANEL_ALT, fg=MUTED,
            relief="flat", font=(FONT_TEXT, 10),
            padx=16, pady=9,
            activebackground=CARD,
            command=self._toggle_autopilot
        )
        self.auto_btn.pack(side="right", padx=4)

    def _build_body(self):
        body = tk.PanedWindow(
            self.root,
            sashwidth=1, sashrelief="flat",
            bg=BORDER, relief="flat"
        )
        body.pack(fill="both", expand=True, padx=24, pady=(10, 0))

        left  = tk.Frame(body, bg=BG)
        right = tk.Frame(body, bg=BG)
        body.add(left,  minsize=920)
        body.add(right, minsize=440)

        self.dashboard_panel = DashboardPanel(left)
        self.dashboard_panel.frame.pack(fill="both", expand=True, pady=(0, 10))

        tk.Frame(left, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(0, 10))

        self.analytics_panel = AnalyticsPanel(left)
        self.analytics_panel.frame.pack(fill="x")

        right_top = tk.Frame(right, bg=BG)
        right_top.pack(fill="both", expand=True, pady=(0, 10))

        tk.Frame(right, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(0, 10))

        right_bot = tk.Frame(right, bg=BG)
        right_bot.pack(fill="both", expand=True)

        self.events_panel = EventsPanel(right_top)
        self.events_panel.frame.pack(fill="both", expand=True)

        self.controls_panel = ControlsPanel(
            right_bot, self._set_speed,
            self._set_pause, self._set_scenario,
        )
        self.controls_panel.frame.pack(fill="both", expand=True)

    def _build_footer(self):
        footer = tk.Frame(self.root, bg=PANEL_ALT)
        footer.pack(fill="x", padx=24, pady=(6, 10))

        self.footer_step = tk.Label(
            footer, text="Step 0 / --",
            bg=PANEL_ALT, fg=DIMMED,
            font=(MONO, 9), padx=14, pady=6
        )
        self.footer_step.pack(side="left")

        tk.Frame(footer, bg=BORDER, width=1).pack(side="left", fill="y", pady=4)

        self.footer_clock = tk.Label(
            footer, text="",
            bg=PANEL_ALT, fg=DIMMED,
            font=(MONO, 9), padx=14, pady=6
        )
        self.footer_clock.pack(side="left")

        tk.Frame(footer, bg=BORDER, width=1).pack(side="left", fill="y", pady=4)

        self.footer_speed = tk.Label(
            footer, text="Speed: 1x",
            bg=PANEL_ALT, fg=DIMMED,
            font=(MONO, 9), padx=14, pady=6
        )
        self.footer_speed.pack(side="left")

        tk.Label(footer,
                 text="Smart Traffic AI  \u2022  Capstone Project  \u2022  2026",
                 bg=PANEL_ALT, fg=DIMMED,
                 font=(MONO, 9), padx=14, pady=6
        ).pack(side="right")

    def _bind_keys(self):
        self.root.bind("<space>",  lambda e: self.controls_panel._toggle_pause())
        self.root.bind("1",        lambda e: self._set_speed(1000))
        self.root.bind("2",        lambda e: self._set_speed(500))
        self.root.bind("3",        lambda e: self._set_speed(250))
        self.root.bind("4",        lambda e: self._set_speed(2000))
        self.root.bind("q",        lambda e: self.root.quit())
        self.root.bind("<Escape>", lambda e: self.root.quit())
        self.root.bind("n",        lambda e: self._set_scenario("normal"))
        self.root.bind("s",        lambda e: self._set_scenario("spoofing"))
        self.root.bind("h",        lambda e: self._set_scenario("heavy"))
        self.root.bind("r",        lambda e: self._set_scenario("recovery"))

    def _set_speed(self, ms):
        self.tick_ms = ms
        labels = {2000: "0.5x", 1000: "1x", 500: "2x", 250: "4x"}
        self.controls_panel._set_speed(labels.get(ms, "?"), ms)
        self.footer_speed.config(text=f"Speed: {labels.get(ms, '?')}")

    def _set_pause(self, paused):
        self.running = not paused

    def _set_scenario(self, scenario):
        self.data_service.set_scenario(scenario)
        self.scenario_badge.config(text=scenario.upper())

    def _toggle_autopilot(self):
        self.autopilot = not self.autopilot
        state = "ON" if self.autopilot else "OFF"
        self.auto_btn.config(
            text=f"Auto Demo  {state}",
            fg=ACCENT if self.autopilot else MUTED
        )

    def _auto_rotate(self, step):
        if not self.autopilot:
            return
        cycle = step % 40
        if   cycle == 0:  self._set_scenario("normal")
        elif cycle == 10: self._set_scenario("heavy")
        elif cycle == 20: self._set_scenario("spoofing")
        elif cycle == 30: self._set_scenario("recovery")

    def _tick(self):
        if self.running and self.data_service.has_data():
            snap    = self.data_service.next()
            summary = self.data_service.summary()
            self._step += 1
            self._auto_rotate(self._step)

            self.dashboard_panel.update(snap)
            self.analytics_panel.update(self.data_service.history, summary)
            self.events_panel.update(self.data_service.events)

            pct = self.data_service.index / self._total_steps * 100
            self.footer_step.config(
                text=f"Step {snap.step} / {self._total_steps - 1}  ({pct:.0f}%)"
            )
            self.footer_clock.config(
                text=datetime.now().strftime("%H:%M:%S")
            )

            if snap.attack_detected:
                self.live_badge.config(text="\u25cf ALERT", fg=DANGER)
            else:
                self.live_badge.config(text="\u25cf LIVE",  fg=SUCCESS)

        self.root.after(self.tick_ms, self._tick)


if __name__ == "__main__":
    root = tk.Tk()
    SmartTrafficDashboard(root)
    root.mainloop()

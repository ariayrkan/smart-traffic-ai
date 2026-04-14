import tkinter as tk
from datetime import datetime
from theme import (
    PANEL, PANEL_ALT, CARD, BORDER,
    TEXT, MUTED, DIMMED,
    SUCCESS, WARNING, DANGER, ACCENT, TEAL,
    FONT, FONT_TEXT, MONO
)


class EventsPanel:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg=PANEL)
        self._last_count = 0

        # Header row
        header = tk.Frame(self.frame, bg=PANEL)
        header.pack(fill="x", padx=20, pady=(18, 0))

        tk.Label(
            header, text="Event Log",
            bg=PANEL, fg=TEXT,
            font=(FONT, 22, "bold")
        ).pack(side="left")

        right = tk.Frame(header, bg=PANEL)
        right.pack(side="right")

        # Event count badge
        self.count_var = tk.StringVar(value="0 events")
        tk.Label(
            right, textvariable=self.count_var,
            bg=PANEL, fg=DIMMED,
            font=(MONO, 9)
        ).pack(side="right", padx=(8, 0))

        # Alert count
        self.alert_var = tk.StringVar(value="")
        tk.Label(
            right, textvariable=self.alert_var,
            bg=PANEL, fg=DANGER,
            font=(MONO, 9, "bold")
        ).pack(side="right")

        tk.Frame(self.frame, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(12, 0))

        # Log text box
        self.box = tk.Text(
            self.frame,
            bg=PANEL_ALT,
            fg=TEXT,
            relief="flat",
            font=(MONO, 10),
            padx=14, pady=12,
            wrap="none",          # no wrap — cleaner log look
            height=18,
            insertbackground=TEXT,
            selectbackground=ACCENT,
            spacing1=3,
            spacing3=3,
        )

        # Horizontal scrollbar for long lines
        xscroll = tk.Scrollbar(self.frame, orient="horizontal",
                               command=self.box.xview, bg=PANEL_ALT)
        self.box.configure(xscrollcommand=xscroll.set)

        self.box.pack(fill="both", expand=True, padx=16, pady=(8, 0))
        xscroll.pack(fill="x", padx=16, pady=(0, 12))

        # Colour tags
        self.box.tag_config("ALERT",  foreground=DANGER,  font=(MONO, 10, "bold"))
        self.box.tag_config("WARN",   foreground=WARNING)
        self.box.tag_config("SYSTEM", foreground=MUTED)
        self.box.tag_config("INFO",   foreground=DIMMED)
        self.box.tag_config("ts",     foreground="#3A3A3C")  # timestamp — very dim

        self.box.configure(state="disabled")
        self._write("[SYSTEM] Event stream online", "SYSTEM")

    def _write(self, line, tag="INFO"):
        self.box.configure(state="normal")
        ts = datetime.now().strftime("%H:%M:%S")
        self.box.insert("end", ts + "  ", "ts")
        self.box.insert("end", line + "\n", tag)
        self.box.see("end")
        self.box.configure(state="disabled")

    def _tag_for(self, line: str) -> str:
        if "[ALERT]"  in line: return "ALERT"
        if "[WARN]"   in line: return "WARN"
        if "[SYSTEM]" in line: return "SYSTEM"
        return "INFO"

    def update(self, events):
        # Only re-render when new events arrive
        if len(events) == self._last_count:
            return
        self._last_count = len(events)

        self.box.configure(state="normal")
        self.box.delete("1.0", "end")

        alert_count = 0
        for line in events[-80:]:
            tag = self._tag_for(line)
            if tag == "ALERT":
                alert_count += 1
            ts = datetime.now().strftime("%H:%M:%S")
            self.box.insert("end", ts + "  ", "ts")
            self.box.insert("end", line + "\n", tag)

        self.box.see("end")
        self.box.configure(state="disabled")

        self.count_var.set(f"{len(events)} events")
        if alert_count:
            self.alert_var.set(f"{alert_count} alerts  ")
        else:
            self.alert_var.set("")

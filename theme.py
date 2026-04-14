"""
Apple-inspired design system tokens.
Dark mode using macOS Ventura / iOS 16 system colors.
"""

# ── Backgrounds (layered depth) ────────────────────────────────
BG          = "#000000"   # true base
SIDEBAR     = "#0A0A0A"   # nav / sidebar layer
PANEL       = "#111111"   # primary surface
PANEL_ALT   = "#1C1C1E"   # elevated surface (Apple UIColor.secondarySystemBackground)
CARD        = "#2C2C2E"   # card fill     (Apple UIColor.tertiarySystemBackground)
CARD_ALT    = "#3A3A3C"   # hover / active state

# ── Borders & dividers ────────────────────────────────────────
BORDER      = "#2C2C2E"   # hairline separator — very subtle
BORDER2     = "#3A3A3C"   # slightly visible

# ── Labels (text hierarchy) ──────────────────────────────────
TEXT        = "#FFFFFF"   # primary label
TEXT2       = "#EBEBF5"   # secondary label (99% white)
MUTED       = "#98989D"   # tertiary label
DIMMED      = "#48484A"   # quaternary / placeholder

# ── System accent colours (Apple exact) ──────────────────────
ACCENT      = "#0A84FF"   # system blue
SUCCESS     = "#30D158"   # system green
WARNING     = "#FFD60A"   # system yellow
DANGER      = "#FF453A"   # system red
ORANGE      = "#FF9F0A"   # system orange
TEAL        = "#5AC8FA"   # system teal

# ── Semantic fills (with alpha baked in for tkinter) ─────────
SUCCESS_DIM = "#0D2B17"   # green/8% on black
WARNING_DIM = "#2B2200"   # yellow/8%
DANGER_DIM  = "#2B0D0B"   # red/8%
ACCENT_DIM  = "#001833"   # blue/8%

# ── Typography ────────────────────────────────────────────────
# Priority order: SF Pro → Helvetica Neue → Segoe UI → system
FONT        = "SF Pro Display"
FONT_TEXT   = "SF Pro Text"
MONO        = "SF Mono"

# tkinter fallback stacks (use first available)
import tkinter.font as tkfont
def _resolve(candidates):
    try:
        avail = set(tkfont.families())
        for f in candidates:
            if f in avail:
                return f
    except Exception:
        pass
    return candidates[-1]

FONT      = _resolve(["SF Pro Display", "Helvetica Neue", ".AppleSystemUIFont", "Segoe UI", "Arial"])
FONT_TEXT = _resolve(["SF Pro Text",    "Helvetica Neue", ".AppleSystemUIFont", "Segoe UI", "Arial"])
MONO      = _resolve(["SF Mono", "Menlo", "Consolas", "Courier New"])

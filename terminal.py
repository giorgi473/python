from __future__ import annotations

import os
import shutil
import sys
import textwrap
import math
from dataclasses import dataclass
from typing import Iterable, Protocol, TypeVar, Any, Sequence

# --- Constants & Basic Colors ---
ANSI_RESET = "\u001b[0m"
ANSI_BOLD = "\u001b[1m"
ANSI_DIM = "\u001b[2m"
ANSI_ITALIC = "\u001b[3m"
ANSI_UNDERLINE = "\u001b[4m"
ANSI_BLINK = "\u001b[5m"
ANSI_REVERSE = "\u001b[7m"
ANSI_HIDDEN = "\u001b[8m"

ANSI_BLACK = "\u001b[30m"
ANSI_RED = "\u001b[31m"
ANSI_GREEN = "\u001b[32m"
ANSI_YELLOW = "\u001b[33m"
ANSI_BLUE = "\u001b[34m"
ANSI_MAGENTA = "\u001b[35m"
ANSI_CYAN = "\u001b[36m"
ANSI_WHITE = "\u001b[37m"

RAINBOW = [ANSI_RED, ANSI_YELLOW, ANSI_GREEN, ANSI_CYAN, ANSI_BLUE, ANSI_MAGENTA]

T = TypeVar("T", bound="Stylable")

class Stylable(Protocol):
    def style(self, **kwargs) -> str: ...

@dataclass(frozen=True)
class RGB:
    r: int
    g: int
    b: int

    def to_ansi(self, background: bool = False) -> str:
        code = 48 if background else 38
        return f"\u001b[{code};2;{self.r};{self.g};{self.b}m"

    @classmethod
    def from_hex(cls, hex_code: str) -> RGB:
        hex_code = hex_code.lstrip("#")
        return cls(*(int(hex_code[i : i + 2], 16) for i in (0, 2, 4)))

# --- Expert Level: Fluent API for Styling ---

class Style:
    """A fluent API for building terminal styles."""
    def __init__(self, color: str | RGB | None = None, bg: str | RGB | None = None, 
                 bold: bool = False, dim: bool = False, italic: bool = False, 
                 underline: bool = False, reverse: bool = False):
        self._color = color
        self._bg = bg
        self._bold = bold
        self._dim = dim
        self._italic = italic
        self._underline = underline
        self._reverse = reverse

    def bold(self) -> Style: return Style(self._color, self._bg, True, self._dim, self._italic, self._underline, self._reverse)
    def dim(self) -> Style: return Style(self._color, self._bg, self._bold, True, self._italic, self._underline, self._reverse)
    def italic(self) -> Style: return Style(self._color, self._bg, self._bold, self._dim, True, self._underline, self._reverse)
    def underline(self) -> Style: return Style(self._color, self._bg, self._bold, self._dim, self._italic, True, self._reverse)
    
    def color(self, color: str | RGB) -> Style:
        return Style(color, self._bg, self._bold, self._dim, self._italic, self._underline, self._reverse)
    
    def on(self, bg: str | RGB) -> Style:
        return Style(self._color, bg, self._bold, self._dim, self._italic, self._underline, self._reverse)

    def apply(self, text: str) -> str:
        codes = []
        if self._bold: codes.append(ANSI_BOLD)
        if self._dim: codes.append(ANSI_DIM)
        if self._italic: codes.append(ANSI_ITALIC)
        if self._underline: codes.append(ANSI_UNDERLINE)
        if self._reverse: codes.append(ANSI_REVERSE)
        
        if self._color:
            codes.append(self._color.to_ansi() if isinstance(self._color, RGB) else self._color)
        if self._bg:
            codes.append(self._bg.to_ansi(background=True) if isinstance(self._bg, RGB) else self._bg)
            
        return f"{''.join(codes)}{text}{ANSI_RESET}"

    def __call__(self, text: str) -> str:
        return self.apply(text)

# --- Innovation: Gradients ---

def gradient_text(text: str, start_rgb: RGB, end_rgb: RGB) -> str:
    """Apply a smooth linear RGB gradient to text."""
    if not text:
        return ""
    result = []
    n = len(text)
    for i, char in enumerate(text):
        if char.isspace():
            result.append(char)
            continue
        # Interpolate RGB
        factor = i / (n - 1) if n > 1 else 0
        r = int(start_rgb.r + (end_rgb.r - start_rgb.r) * factor)
        g = int(start_rgb.g + (end_rgb.g - start_rgb.g) * factor)
        b = int(start_rgb.b + (end_rgb.b - start_rgb.b) * factor)
        result.append(f"{RGB(r, g, b).to_ansi()}{char}")
    return "".join(result) + ANSI_RESET

# --- Core Utility Functions (Refined) ---

def terminal_width(default: int = 80) -> int:
    """Get the current terminal width in columns."""
    try:
        return shutil.get_terminal_size((default, 20)).columns
    except (OSError, ValueError):
        return default

def supports_color() -> bool:
    """Return True when the current terminal should support ANSI color."""
    if os.environ.get("NO_COLOR"):
        return False
    if sys.platform.startswith("win"):
        # Modern Windows Terminal or VSCode support colors out of the box
        return "ANSICON" in os.environ or "WT_SESSION" in os.environ or \
               os.environ.get("TERM_PROGRAM") == "vscode" or \
               os.environ.get("TERM") == "xterm-256color"
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

def clear_screen() -> None:
    """Clear the terminal screen and reset cursor position."""
    if sys.platform.startswith("win"):
        os.system("cls")
    else:
        print("\033[2J\033[H", end="", flush=True)

def style_text(
    text: str,
    color: str = ANSI_RESET,
    bold: bool = False,
    dim: bool = False,
    underline: bool = False,
) -> str:
    """Style text with ANSI attributes (Legacy compatible)."""
    s = Style(color=color, bold=bold, dim=dim, underline=underline)
    return s.apply(text)

def render_progress_bar(
    fraction: float,
    length: int = 30,
    fill_char: str = "█",
    empty_char: str = "░",
    color: str = ANSI_GREEN,
) -> str:
    """Render a high-fidelity progress bar."""
    fraction = max(0.0, min(1.0, fraction))
    filled_len = int(length * fraction)
    
    # Use subtle characters for empty space for a modern look
    filled = f"{color}{fill_char * filled_len}{ANSI_RESET}"
    empty = f"{ANSI_DIM}{empty_char * (length - filled_len)}{ANSI_RESET}"
    
    percent = f"{int(fraction * 100):>3}%"
    return f"▕{filled}{empty}▏ {percent}"

def render_metric_bar(value: float, max_value: float = 100.0, length: int = 24, color: str = ANSI_GREEN) -> str:
    """Render a metric progress bar for values like memory or load."""
    if max_value <= 0:
        return f"{ANSI_RED}[Invalid]{ANSI_RESET}"
    return render_progress_bar(value / max_value, length=length, color=color)

def render_centered(text: str, width: int | None = None) -> str:
    """Center text within the terminal width."""
    width = width or terminal_width()
    # Strip ANSI codes for length calculation
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    plain_text = ansi_escape.sub('', text)
    padding = max(0, (width - len(plain_text)) // 2)
    return " " * padding + text

def rainbow_text(text: str) -> str:
    """Apply vibrant rainbow colors to text."""
    return "".join(RAINBOW[i % len(RAINBOW)] + char for i, char in enumerate(text)) + ANSI_RESET

def wrap_text(text: str, width: int | None = None, indent: int = 0) -> str:
    """Wrap text to fit within width, with optional indent."""
    width = width or terminal_width()
    if width <= indent + 10:
        return text
    wrapper = textwrap.TextWrapper(
        width=width - indent, 
        initial_indent=" " * indent, 
        subsequent_indent=" " * indent,
        break_long_words=False,
        replace_whitespace=False
    )
    return wrapper.fill(text)

# --- Advanced Components ---

def render_box(text: str, title: str | None = None, color: str = ANSI_CYAN, width: int | None = None) -> str:
    """Wrap text in a modern Unicode box."""
    width = width or min(terminal_width(), 80)
    inner_width = width - 4
    lines = wrap_text(text, width=inner_width).splitlines()
    
    top = f"╭─{' ' + title + ' ' if title else ''}{'─' * (inner_width - (len(title) + 2) if title else inner_width)}─╮"
    bottom = f"╰{'─' * (inner_width + 2)}╯"
    
    output = [f"{color}{top}{ANSI_RESET}"]
    for line in lines:
        output.append(f"{color}│{ANSI_RESET} {line.ljust(inner_width)} {color}│{ANSI_RESET}")
    output.append(f"{color}{bottom}{ANSI_RESET}")
    
    return "\n".join(output)

def render_table(rows: list[list[Any]], headers: list[str], padding: int = 2) -> str:
    """Render a sophisticated table with Unicode borders."""
    if not headers:
        return ""
        
    # Prepare data
    data = [[str(cell) for cell in row] for row in rows]
    all_rows = [headers] + data
    
    # Calculate widths
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    def visible_len(s: str) -> int:
        return len(ansi_escape.sub('', s))

    col_widths = [
        max(visible_len(row[i]) if i < len(row) else 0 for row in all_rows)
        for i in range(len(headers))
    ]
    
    # Borders
    top = "┌─" + "─┬─".join("─" * w for w in col_widths) + "─┐"
    mid = "├─" + "─┼─".join("─" * w for w in col_widths) + "─┤"
    bot = "└─" + "─┴─".join("─" * w for w in col_widths) + "─┘"
    
    def format_row(row: list[str]) -> str:
        cells = []
        for i, cell in enumerate(row):
            w = col_widths[i]
            diff = w - visible_len(cell)
            cells.append(cell + " " * diff)
        return "│ " + " │ ".join(cells) + " │"

    output = [top, format_row(headers), mid]
    for row in data:
        output.append(format_row(row))
    output.append(bot)
    
    return "\n".join(output)

def humanize_bytes(value: int, precision: int = 1, binary: bool = True) -> str:
    """Convert bytes into a human readable string with modern defaults."""
    sign = "-" if value < 0 else ""
    value = abs(value)
    base = 1024 if binary else 1000
    units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"] if binary else ["B", "KB", "MB", "GB", "TB", "PB"]
    
    if value < base:
        return f"{sign}{value}{units[0]}"
        
    unit_idx = int(math.log(value, base))
    unit_idx = min(unit_idx, len(units) - 1)
    scaled = value / (base ** unit_idx)
    
    return f"{sign}{scaled:.{precision}f}{units[unit_idx]}"

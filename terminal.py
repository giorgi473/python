from __future__ import annotations

import shutil

ANSI_RESET = "\u001b[0m"
ANSI_BOLD = "\u001b[1m"
ANSI_BLUE = "\u001b[34m"
ANSI_CYAN = "\u001b[36m"
ANSI_GREEN = "\u001b[32m"
ANSI_MAGENTA = "\u001b[35m"
ANSI_YELLOW = "\u001b[33m"
ANSI_RED = "\u001b[31m"
ANSI_WHITE = "\u001b[37m"
ANSI_DIM = "\u001b[2m"

RAINBOW = [ANSI_RED, ANSI_YELLOW, ANSI_GREEN, ANSI_CYAN, ANSI_BLUE, ANSI_MAGENTA]


def terminal_width(default: int = 80) -> int:
    """Get the current terminal width in columns."""
    return shutil.get_terminal_size((default, 20)).columns


def clear_screen() -> None:
    """Clear the terminal screen."""
    print("\033[2J\033[H", end="")


def render_progress_bar(fraction: float, length: int = 30, fill_char: str = "█", color: str = ANSI_GREEN) -> str:
    """Render a progress bar as a string."""
    fraction = max(0.0, min(1.0, fraction))
    filled = int(fraction * length)
    empty = length - filled
    percent = f"{int(fraction * 100):3d}%"
    return f"[{color}{fill_char * filled}{ANSI_RESET}{' ' * empty}] {percent}"


def render_metric_bar(value: float, max_value: float = 100.0, length: int = 24, color: str = ANSI_GREEN) -> str:
    """Render a metric progress bar for values like memory or load."""
    if max_value <= 0:
        return "[Invalid]"
    fraction = max(0.0, min(1.0, value / max_value))
    return render_progress_bar(fraction, length=length, color=color)


def render_centered(text: str, width: int | None = None) -> str:
    """Center text within the terminal width."""
    width = width or terminal_width()
    return text.center(width)


def rainbow_text(text: str) -> str:
    """Apply rainbow colors to text."""
    return "".join(RAINBOW[i % len(RAINBOW)] + char for i, char in enumerate(text)) + ANSI_RESET


def wrap_text(text: str, width: int | None = None, indent: int = 0) -> str:
    """Wrap text to fit within width, with optional indent."""
    width = width or terminal_width()
    if width <= indent + 20:
        return text
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 > width - indent:
            lines.append(current.rstrip())
            current = " " * indent + word + " "
        else:
            current += word + " "
    if current:
        lines.append(current.rstrip())
    return "\n".join(lines)

from __future__ import annotations

import shutil

ANSI_RESET = "\u001b[0m"
ANSI_BOLD = "\u001b[1m"
ANSI_CYAN = "\u001b[36m"
ANSI_GREEN = "\u001b[32m"
ANSI_MAGENTA = "\u001b[35m"
ANSI_YELLOW = "\u001b[33m"
ANSI_BLUE = "\u001b[34m"


def render_progress_bar(fraction: float, length: int = 30) -> str:
    filled = int(fraction * length)
    empty = length - filled
    return f"[{ANSI_GREEN}{'█' * filled}{ANSI_RESET}{' ' * empty}]"


def terminal_width(default: int = 80) -> int:
    return shutil.get_terminal_size((default, 20)).columns

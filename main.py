#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import datetime
import os
import platform
import random
import shutil
import sys
import time
from dataclasses import dataclass
from typing import Callable, Dict

ANSI_RESET = "\u001b[0m"
ANSI_BOLD = "\u001b[1m"
ANSI_CYAN = "\u001b[36m"
ANSI_GREEN = "\u001b[32m"
ANSI_MAGENTA = "\u001b[35m"
ANSI_YELLOW = "\u001b[33m"
ANSI_BLUE = "\u001b[34m"

@dataclass(frozen=True)
class Command:
    name: str
    label: str
    description: str
    handler: Callable[[], asyncio.Future[None]]


class ModernWorkbench:
    def __init__(self) -> None:
        self.commands: Dict[str, Command] = {
            "status": Command(
                name="status",
                label="System Pulse",
                description="Show live system and environment information.",
                handler=self.show_system_pulse,
            ),
            "idea": Command(
                name="idea",
                label="Creative Spark",
                description="Generate a modern project idea or productivity prompt.",
                handler=self.generate_innovation_prompt,
            ),
            "timer": Command(
                name="timer",
                label="Focus Timer",
                description="Run a short countdown with progress feedback.",
                handler=self.run_focus_timer,
            ),
            "demo": Command(
                name="demo",
                label="Visual Flow",
                description="Render a dynamic command palette preview.",
                handler=self.render_command_palette,
            ),
        }

    async def run(self, args: argparse.Namespace) -> None:
        if args.command:
            await self.execute(args.command)
            return

        await self.interactive_shell()

    async def execute(self, command_name: str) -> None:
        command = self.commands.get(command_name)
        if command is None:
            self.print_header("Oops! Unknown command", style=ANSI_YELLOW)
            print(f"Available commands: {', '.join(self.commands)}")
            return
        await command.handler()

    async def interactive_shell(self) -> None:
        self.print_header("Modern Workbench", style=ANSI_CYAN)
        self.print_subtitle("Type a command name or press Enter to see the menu.")

        while True:
            self.print_menu()
            selection = input(f"{ANSI_BOLD}> {ANSI_RESET}").strip().lower()
            if selection in {"quit", "exit", "q"}:
                print("Goodbye. Stay productive! ✨")
                return
            if selection == "":
                continue
            await self.execute(selection)
            print()

    def print_header(self, text: str, style: str = ANSI_GREEN) -> None:
        width = shutil.get_terminal_size((80, 20)).columns
        border = style + "=" * width + ANSI_RESET
        print(border)
        print(style + ANSI_BOLD + text.center(width) + ANSI_RESET)
        print(border)

    def print_subtitle(self, text: str) -> None:
        print(ANSI_MAGENTA + text + ANSI_RESET)
        print()

    def print_menu(self) -> None:
        self.print_header("Command Palette")
        for command in self.commands.values():
            print(f"{ANSI_BLUE}{command.name:<8}{ANSI_RESET} {command.label} - {command.description}")
        print(f"{ANSI_BLUE}exit{ANSI_RESET}    Quit the workbench")
        print()

    async def show_system_pulse(self) -> None:
        self.print_header("System Pulse")
        meta = {
            "Timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
            "Platform": platform.system(),
            "Release": platform.release(),
            "Python": platform.python_version(),
            "CPU Count": os.cpu_count() or "unknown",
            "Working Directory": os.getcwd(),
        }
        for label, value in meta.items():
            print(f"{ANSI_BOLD}{label:<18}{ANSI_RESET} {value}")

        if sys.platform.startswith("win"):
            print(f"{ANSI_MAGENTA}Tip:{ANSI_RESET} For best visuals, use Windows Terminal or PowerShell 7+.")

    async def generate_innovation_prompt(self) -> None:
        self.print_header("Creative Spark")
        prompts = [
            "Build a lightweight habit tracker that rewards streaks with animated terminal badges.",
            "Create a personal dashboard that turns your local files into a productivity game.",
            "Design a smart note-taker that tags ideas with emotion, priority, and follow-up actions.",
            "Prototype a context-aware CLI that suggests the next task based on your calendar and focus windows.",
        ]
        prompt = random.choice(prompts)
        print(ANSI_GREEN + prompt + ANSI_RESET)
        print()
        print(ANSI_YELLOW + "Next step:" + ANSI_RESET + " Press Enter to keep generating or type any command to continue.")

    async def run_focus_timer(self) -> None:
        self.print_header("Focus Timer")
        duration = 10
        for elapsed in range(duration + 1):
            progress = elapsed / duration
            bar = self.render_progress_bar(progress)
            remaining = duration - elapsed
            print(f"{ANSI_BOLD}Focus progress:{ANSI_RESET} {bar} {remaining}s remaining", end="\r", flush=True)
            await asyncio.sleep(1)
        print()
        print(ANSI_GREEN + "Focus session complete! Take a quick break. ☕" + ANSI_RESET)

    async def render_command_palette(self) -> None:
        self.print_header("Visual Flow")
        width = shutil.get_terminal_size((80, 20)).columns
        flow = ["Idea", "Draft", "Review", "Ship"]
        line = " → ".join(flow)
        padding = max(0, (width - len(line)) // 2)
        print(" " * padding + ANSI_CYAN + line + ANSI_RESET)
        print()
        print(ANSI_MAGENTA + "Toolchain:" + ANSI_RESET + " Async, typed, and terminal-friendly.")

    def render_progress_bar(self, fraction: float, length: int = 30) -> str:
        filled = int(fraction * length)
        empty = length - filled
        return f"[{ANSI_GREEN}{'█' * filled}{ANSI_RESET}{' ' * empty}]"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Modern terminal workbench with async functionality.")
    parser.add_argument("--command", "-c", help="Run a single command without the interactive shell.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    workbench = ModernWorkbench()
    try:
        asyncio.run(workbench.run(args))
    except KeyboardInterrupt:
        print("\nInterrupted. See you soon!")


if __name__ == "__main__":
    main()

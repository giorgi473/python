from __future__ import annotations

import argparse
import asyncio
import datetime
import difflib
import os
import platform
import random
import shutil
import subprocess
import sys
from typing import List, Optional, Sequence

from commands import Command
from terminal import (
    ANSI_BLUE,
    ANSI_BOLD,
    ANSI_CYAN,
    ANSI_GREEN,
    ANSI_MAGENTA,
    ANSI_RED,
    ANSI_RESET,
    ANSI_YELLOW,
    clear_screen,
    rainbow_text,
    render_centered,
    render_progress_bar,
    terminal_width,
    wrap_text,
)


class ModernWorkbench:
    def __init__(self) -> None:
        self.commands: List[Command] = []
        self.history: List[str] = []

        self.register_command(
            Command(
                name="status",
                label="System Pulse",
                description="Show live system and environment information.",
                handler=self.show_system_pulse,
                aliases=("sys", "pulse", "info"),
            )
        )
        self.register_command(
            Command(
                name="idea",
                label="Creative Spark",
                description="Generate a modern project idea or productivity prompt.",
                handler=self.generate_innovation_prompt,
                aliases=("spark", "prompt"),
            )
        )
        self.register_command(
            Command(
                name="timer",
                label="Focus Timer",
                description="Run a countdown, quick timer, or Pomodoro cycle.",
                handler=self.run_focus_timer,
                aliases=("focus", "pomodoro"),
            )
        )
        self.register_command(
            Command(
                name="demo",
                label="Visual Flow",
                description="Render an adaptive command palette preview.",
                handler=self.render_command_palette,
                aliases=("show", "view"),
            )
        )
        self.register_command(
            Command(
                name="history",
                label="Command History",
                description="Review the commands you've executed this session.",
                handler=self.show_history,
                aliases=("log",),
            )
        )

    def register_command(self, command: Command) -> None:
        self.commands.append(command)

    def find_command(self, token: str) -> Optional[Command]:
        for command in self.commands:
            if command.matches(token):
                return command
        return None

    def suggest_commands(self, token: str) -> List[str]:
        names = [command.name for command in self.commands if not command.hidden]
        suggestions = difflib.get_close_matches(token, names, n=3, cutoff=0.4)
        return suggestions

    async def run(self, args: argparse.Namespace) -> None:
        if args.command:
            await self.execute(args.command, args.args)
            return

        clear_screen()
        self.print_header("Modern Workbench", style=ANSI_CYAN)
        self.print_subtitle("Type a command name, or enter 'help' for the palette.")

        await self.interactive_shell()

    async def execute(self, command_name: str, argv: Sequence[str] = ()) -> None:
        command = self.find_command(command_name)
        if command is None:
            self.print_header("Unknown command", style=ANSI_YELLOW)
            print(f"{ANSI_BOLD}{command_name}{ANSI_RESET} is not in the palette.")
            suggestions = self.suggest_commands(command_name)
            if suggestions:
                print(f"Did you mean: {ANSI_GREEN}{', '.join(suggestions)}{ANSI_RESET}?"
)
            print("Type 'help' to open the command palette.")
            return

        self.history.append(" ".join([command_name, *list(argv)]).strip())
        await command.handler(argv)

    async def interactive_shell(self) -> None:
        while True:
            selection = input(f"{ANSI_BOLD}> {ANSI_RESET}").strip()
            if not selection:
                self.print_menu()
                continue

            normalized = selection.lower()
            if normalized in {"quit", "exit", "q"}:
                print("Goodbye. Stay productive! ✨")
                return
            if normalized in {"help", "menu", "list"}:
                self.print_menu()
                continue
            if normalized in {"clear", "cls"}:
                clear_screen()
                continue

            parts = selection.split()
            await self.execute(parts[0], parts[1:])
            print()

    def print_header(self, text: str, style: str = ANSI_GREEN) -> None:
        width = terminal_width()
        border = style + "=" * width + ANSI_RESET
        print(border)
        print(style + ANSI_BOLD + text.center(width) + ANSI_RESET)
        print(border)

    def print_subtitle(self, text: str) -> None:
        print(ANSI_MAGENTA + wrap_text(text, indent=2) + ANSI_RESET)
        print()

    def print_menu(self) -> None:
        self.print_header("Command Palette")
        for command in self.commands:
            if command.hidden:
                continue
            aliases = f" ({', '.join(command.aliases)})" if command.aliases else ""
            print(f"{ANSI_BLUE}{command.name:<10}{ANSI_RESET} {command.label}{aliases} - {command.description}")
        print(f"{ANSI_BLUE}exit{ANSI_RESET}     Quit the workbench")
        print(f"{ANSI_BLUE}clear{ANSI_RESET}    Clear the screen")
        print()

    async def show_system_pulse(self, argv: Sequence[str]) -> None:
        self.print_header("System Pulse")
        metadata = {
            "Timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
            "Platform": platform.system(),
            "Release": platform.release(),
            "Python": platform.python_version(),
            "CPU Count": os.cpu_count() or "unknown",
            "Working Directory": os.getcwd(),
        }

        if hasattr(os, "getloadavg"):
            load_avg = os.getloadavg()
            metadata["Load Average"] = ", ".join(f"{value:.2f}" for value in load_avg)

        git_branch = self.detect_git_branch()
        if git_branch:
            metadata["Git Branch"] = git_branch

        for label, value in metadata.items():
            print(f"{ANSI_BOLD}{label:<18}{ANSI_RESET} {value}")

        if sys.platform.startswith("win"):
            print()
            print(f"{ANSI_MAGENTA}Tip:{ANSI_RESET} For best visuals, use Windows Terminal or PowerShell 7+.")

    def detect_git_branch(self) -> Optional[str]:
        if shutil.which("git") is None:
            return None
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                text=True,
                capture_output=True,
                cwd=os.getcwd(),
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    async def generate_innovation_prompt(self, argv: Sequence[str]) -> None:
        self.print_header("Creative Spark")
        themes = [
            {
                "title": "Terminal Zen",
                "idea": "Build a distraction-free CLI that rewards progress with ambient animations and smart goal nudges.",
                "steps": [
                    "Map your daily habits to tiny terminal badges.",
                    "Create a command mode for quick notes, timers, and micro-sprints.",
                    "Add an inspiration engine that chooses tasks based on emotion and energy.",
                ],
            },
            {
                "title": "Local Intelligence",
                "idea": "Create a personal assistant that reads your workspace context and suggests the next best action.",
                "steps": [
                    "Scan open files and recent commands to spot patterns.",
                    "Offer a one-line focus prompt for each working session.",
                    "Surface follow-up tasks automatically at the end of each sprint.",
                ],
            },
            {
                "title": "Playful Productivity",
                "idea": "Design a CLI game where building habits unlocks terminal cosmetics, witty feedback, and hidden easter eggs.",
                "steps": [
                    "Track streaks and milestone achievements.",
                    "Reward focus sessions with animated badges.",
                    "Hide secret commands and surprise prompts for the curious user.",
                ],
            },
        ]

        choice = random.choice(themes)
        print(ANSI_BOLD + choice["title"] + ANSI_RESET)
        print(choice["idea"])
        print()
        for step in choice["steps"]:
            print(f"{ANSI_CYAN}•{ANSI_RESET} {step}")

        print()
        print(ANSI_YELLOW + "Tip:" + ANSI_RESET + " Use `idea` again to generate a new spark or combine prompts into one bold project.")

    async def run_focus_timer(self, argv: Sequence[str]) -> None:
        self.print_header("Focus Timer")
        duration = 25
        cycles = 1

        if argv:
            first = argv[0].lower()
            if first.isdigit():
                duration = max(1, min(180, int(first)))
            elif first in {"short", "quick", "tiny"}:
                duration = 5
            elif first in {"focus", "work"}:
                duration = 25
            elif first in {"pomodoro", "pomo"}:
                duration = 25

        if len(argv) > 1 and argv[1].isdigit():
            cycles = max(1, min(8, int(argv[1])))

        total_seconds = duration * cycles
        print(f"{ANSI_MAGENTA}Session:{ANSI_RESET} {duration} seconds × {cycles} cycle(s) = {total_seconds} seconds")

        for cycle in range(1, cycles + 1):
            print(f"{ANSI_BLUE}Cycle {cycle}/{cycles}{ANSI_RESET}")
            for elapsed in range(duration + 1):
                progress = elapsed / duration
                bar = render_progress_bar(progress, length=32)
                remaining = duration - elapsed
                print(f"{ANSI_BOLD}Focus:{ANSI_RESET} {bar} {remaining}s remaining", end="\r", flush=True)
                await asyncio.sleep(1)
            print()
            if cycle < cycles:
                print(ANSI_YELLOW + "Take a short pause and prepare for the next cycle." + ANSI_RESET)
                await asyncio.sleep(2)

        print(ANSI_GREEN + "Focus session complete! Take a short break and reflect on progress. ☕" + ANSI_RESET)

    async def render_command_palette(self, argv: Sequence[str]) -> None:
        self.print_header("Visual Flow")
        width = terminal_width()
        steps = ["Spark", "Sketch", "Focus", "Ship"]
        rendered = "  ".join(f"{ANSI_CYAN}[ {step} ]{ANSI_RESET}" for step in steps)
        print(render_centered(rendered, width))
        print()
        banner = rainbow_text("THE MOST MODERN COMMAND HUB")
        print(render_centered(banner, width))
        print()
        print(ANSI_MAGENTA + wrap_text("This palette adapts to your terminal width and gives you an energizing flow for creative work.", width=width, indent=2) + ANSI_RESET)

    async def show_history(self, argv: Sequence[str]) -> None:
        self.print_header("Command History")
        if not self.history:
            print(ANSI_YELLOW + "No commands executed yet. Start with `status` or `idea`." + ANSI_RESET)
            return
        for index, record in enumerate(self.history, start=1):
            print(f"{ANSI_GREEN}{index:>2}.{ANSI_RESET} {record}")

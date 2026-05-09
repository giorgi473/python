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
        self.register_command(
            Command(
                name="workspace",
                label="Workspace Insight",
                description="Analyze the current project folder and suggest structure improvements.",
                handler=self.inspect_workspace,
                aliases=("inspect", "analyze"),
            )
        )
        self.register_command(
            Command(
                name="shell",
                label="Shell Runner",
                description="Run a shell command and stream live terminal output.",
                handler=self.run_shell_command,
                aliases=("run", "exec", "cmd"),
            )
        )
        self.register_command(
            Command(
                name="boost",
                label="Momentum Booster",
                description="Generate a high-energy focus prompt with a clear action plan.",
                handler=self.generate_momentum_prompt,
                aliases=("mood", "hype"),
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
            if selection.startswith("!"):
                await self.execute("shell", [selection[1:].strip()])
                print()
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

        disk = shutil.disk_usage(os.getcwd())
        metadata["Disk Usage"] = f"{disk.used // (1024 ** 3)}GB / {disk.total // (1024 ** 3)}GB"
        metadata["Workspace Files"] = sum(len(files) for _, _, files in os.walk(os.getcwd()))

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

    async def stream_subprocess_output(self, stream: asyncio.StreamReader, prefix: str = "") -> None:
        while True:
            line = await stream.readline()
            if not line:
                break
            text = line.decode(errors="replace").rstrip()
            print(f"{prefix}{text}{ANSI_RESET if prefix else ""}")

    async def run_shell_command(self, argv: Sequence[str]) -> None:
        self.print_header("Shell Runner")
        if argv:
            command_text = " ".join(argv)
        else:
            command_text = input("Shell command: ").strip()
            if not command_text:
                print(ANSI_YELLOW + "No shell command provided. Try `shell echo hello` or `!dir`." + ANSI_RESET)
                return

        print(ANSI_DIM + f"Executing:{ANSI_RESET} {command_text}")
        process = await asyncio.create_subprocess_shell(
            command_text,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        assert process.stdout is not None and process.stderr is not None
        tasks = [
            asyncio.create_task(self.stream_subprocess_output(process.stdout)),
            asyncio.create_task(self.stream_subprocess_output(process.stderr, ANSI_RED)),
        ]
        await asyncio.wait(tasks)
        return_code = await process.wait()
        result_color = ANSI_GREEN if return_code == 0 else ANSI_RED
        print(result_color + f"Process exited with code {return_code}." + ANSI_RESET)

    async def inspect_workspace(self, argv: Sequence[str]) -> None:
        self.print_header("Workspace Insight")
        root = os.getcwd()
        extension_counts: dict[str, int] = {}
        largest_files: list[tuple[int, str]] = []
        markers: set[str] = set()

        marker_names = {
            "pyproject.toml",
            "requirements.txt",
            "package.json",
            "tsconfig.json",
            "README.md",
            ".gitignore",
        }

        for dirpath, _, filenames in os.walk(root):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                ext = os.path.splitext(filename)[1].lower() or "<none>"
                extension_counts[ext] = extension_counts.get(ext, 0) + 1
                try:
                    size = os.path.getsize(filepath)
                except OSError:
                    continue
                largest_files.append((size, os.path.relpath(filepath, root)))
                if filename in marker_names:
                    markers.add(filename)

        largest_files.sort(reverse=True)
        total_files = sum(extension_counts.values())
        top_types = sorted(extension_counts.items(), key=lambda item: item[1], reverse=True)[:5]

        project_type = "Mixed / unknown"
        if "package.json" in markers or "tsconfig.json" in markers:
            project_type = "Node.js / TypeScript"
        elif "pyproject.toml" in markers or "requirements.txt" in markers or any(ext == ".py" for ext in extension_counts):
            project_type = "Python"

        print(f"{ANSI_BOLD}Root:{ANSI_RESET} {root}")
        print(f"{ANSI_BOLD}Detected Project Type:{ANSI_RESET} {project_type}")
        print(f"{ANSI_BOLD}Total files scanned:{ANSI_RESET} {total_files}")
        print(f"{ANSI_BOLD}Markers found:{ANSI_RESET} {', '.join(sorted(markers)) or 'none'}")
        print()

        print(ANSI_CYAN + "Top file types:" + ANSI_RESET)
        for ext, count in top_types:
            print(f"  {ANSI_GREEN}{ext or '<none>'}{ANSI_RESET}: {count}")

        print()
        print(ANSI_CYAN + "Largest files:" + ANSI_RESET)
        for size, relative in largest_files[:5]:
            print(f"  {ANSI_BLUE}{relative}{ANSI_RESET} — {size // 1024} KB")

        print()
        recommendations = []
        if project_type == "Python" and "README.md" in markers:
            recommendations.append("Add a short usage example to README.md.")
        if project_type == "Node.js / TypeScript" and "package.json" in markers:
            recommendations.append("Consider adding a script shortcut for build or test.")
        if not markers:
            recommendations.append("Track the workspace with a README and git for instant confidence.")

        for recommendation in recommendations:
            print(f"{ANSI_YELLOW}Tip:{ANSI_RESET} {recommendation}")

    async def generate_momentum_prompt(self, argv: Sequence[str]) -> None:
        self.print_header("Momentum Booster")
        boosts = [
            {
                "title": "Spike the sprint",
                "idea": "Choose one small feature, remove the noise, and ship it now.",
                "plan": [
                    "Define the smallest useful slice.",
                    "Work without distractions for one focused cycle.",
                    "Review only the result, not the process.",
                ],
            },
            {
                "title": "Polish the edge",
                "idea": "Pick the part that feels hardest and make it feel effortless.",
                "plan": [
                    "Identify the friction point.",
                    "Simplify the behavior until it feels natural.",
                    "Celebrate the tiny win with a note.",
                ],
            },
            {
                "title": "Launch a micro-experiment",
                "idea": "Build a minimal version of one bold idea and gather feedback fast.",
                "plan": [
                    "Write the simplest possible prototype.",
                    "Share it with one person or one channel.",
                    "Refine based on the first response.",
                ],
            },
        ]

        selection = random.choice(boosts)
        print(ANSI_BOLD + selection["title"] + ANSI_RESET)
        print(selection["idea"])
        print()
        for step in selection["plan"]:
            print(f"{ANSI_CYAN}→{ANSI_RESET} {step}")

        print()
        print(ANSI_YELLOW + "Use `boost` again when you need fresh energy or a new angle." + ANSI_RESET)

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

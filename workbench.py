from __future__ import annotations

import argparse
import asyncio
import datetime
import difflib
import fnmatch
import math
import os
import platform
import random
import re
import shutil
import subprocess
import sys
import time
from collections import Counter
from typing import List, Optional, Sequence

try:
    import readline
except ImportError:  # pragma: no cover
    readline = None

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
    render_metric_bar,
    render_progress_bar,
    terminal_width,
    wrap_text,
)


class ModernWorkbench:
    """A modern terminal-based workbench for productivity and system management."""

    def __init__(self) -> None:
        self.commands: List[Command] = []
        self.history: List[str] = []
        self.session_start = time.monotonic()

        self.register_command(
            Command(
                name="status",
                label="System Pulse",
                description="Show live system and environment information.",
                handler=self.show_system_pulse,
                aliases=("sys", "pulse", "info", "pulsecheck"),
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
                aliases=("focus", "pomodoro", "pomo"),
            )
        )
        self.register_command(
            Command(
                name="demo",
                label="Visual Flow",
                description="Render an adaptive command palette preview.",
                handler=self.render_command_palette,
                aliases=("show", "view", "palette"),
            )
        )
        self.register_command(
            Command(
                name="history",
                label="Command History",
                description="Review the commands you've executed this session.",
                handler=self.show_history,
                aliases=("log", "recent"),
            )
        )
        self.register_command(
            Command(
                name="workspace",
                label="Workspace Insight",
                description="Analyze the current project folder and suggest structure improvements.",
                handler=self.inspect_workspace,
                aliases=("inspect", "analyze", "audit", "radar"),
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
                aliases=("mood", "hype", "charge"),
            )
        )
        self.register_command(
            Command(
                name="version",
                label="Version Info",
                description="Show the workbench version.",
                handler=self.show_version,
                aliases=("ver", "about"),
            )
        )
        self.register_command(
            Command(
                name="search",
                label="Smart Finder",
                description="Perform an intelligent search across files with live previews and context.",
                handler=self.smart_search,
                aliases=("find", "grep", "seek"),
            )
        )
        self.register_command(
            Command(
                name="secret",
                label="Secret Magic",
                description="Reveal a hidden easter egg and surprise workspace insight.",
                handler=self.reveal_secret,
                aliases=("magic", "easter", "hidden"),
                hidden=True,
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

    def readline_completer(self, text: str, state: int) -> Optional[str]:
        if readline is None:
            return None
        options = [command.name for command in self.commands if command.name.startswith(text)]
        options += [alias for command in self.commands for alias in command.aliases if alias.startswith(text)]
        options = sorted(set(options))
        return options[state] if state < len(options) else None

    def setup_readline(self) -> None:
        if readline is None:
            return
        try:
            readline.parse_and_bind("tab: complete")
            readline.set_completer(self.readline_completer)
        except Exception:
            pass

    def print_welcome(self) -> None:
        self.print_header("Modern Workbench", style=ANSI_CYAN)
        self.print_subtitle(
            "Type a command, use 'help' for the palette, prefix a command with '!' to run shell commands, or discover the hidden magic."
        )

    async def run(self, args: argparse.Namespace) -> None:
        if args.run:
            await self.execute(args.run, args.args)
            return

        clear_screen()
        self.setup_readline()
        self.print_welcome()

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
            try:
                selection = input(f"{ANSI_BOLD}> {ANSI_RESET}").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                print("Goodbye. Stay productive! ✨")
                return

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
        branch, git_status = self.detect_git_status()

        metadata = {
            "Timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
            "Platform": platform.system(),
            "Release": platform.release(),
            "Python": platform.python_version(),
            "CPU Count": os.cpu_count() or "unknown",
            "Working Directory": os.getcwd(),
            "Session Uptime": self.session_uptime(),
            "Workspace Files": sum(len(files) for _, _, files in os.walk(os.getcwd())),
        }

        if branch:
            metadata["Git Branch"] = branch
        if git_status:
            metadata["Git Status"] = git_status

        if hasattr(os, "getloadavg"):
            load_avg = os.getloadavg()
            metadata["Load Average"] = ", ".join(f"{value:.2f}" for value in load_avg)
            print(f"{ANSI_BOLD}Load 1m:{ANSI_RESET} {render_metric_bar(load_avg[0], max_value=4.0)}")
            print(f"{ANSI_BOLD}Load 5m:{ANSI_RESET} {render_metric_bar(load_avg[1], max_value=4.0)}")
            print(f"{ANSI_BOLD}Load15m:{ANSI_RESET} {render_metric_bar(load_avg[2], max_value=4.0)}")
            print()

        memory_summary, memory_bar = self.get_memory_summary()
        if memory_summary:
            print(f"{ANSI_BOLD}Memory:{ANSI_RESET} {memory_summary} {memory_bar}")

        disk = shutil.disk_usage(os.getcwd())
        disk_summary = f"{self.humanize_bytes(disk.used)} / {self.humanize_bytes(disk.total)}"
        print(f"{ANSI_BOLD}Disk Usage:{ANSI_RESET} {disk_summary} {render_metric_bar(disk.used / disk.total * 100, max_value=100.0)}")
        print()

        for label, value in metadata.items():
            if label in {"Workspace Files"}:
                print(f"{ANSI_BOLD}{label:<18}{ANSI_RESET} {value}")
                continue
            if label not in {"Git Status"}:
                print(f"{ANSI_BOLD}{label:<18}{ANSI_RESET} {value}")
        if git_status:
            print(f"{ANSI_BOLD}Git Status:{ANSI_RESET} {git_status}")

        if sys.platform.startswith("win"):
            print()
            print(f"{ANSI_MAGENTA}Tip:{ANSI_RESET} For best visuals, use Windows Terminal or PowerShell 7+.")

    def detect_git_status(self) -> tuple[Optional[str], Optional[str]]:
        if shutil.which("git") is None:
            return None, None
        try:
            branch_result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                text=True,
                capture_output=True,
                cwd=os.getcwd(),
                check=True,
            )
            branch = branch_result.stdout.strip()

            status_result = subprocess.run(
                ["git", "status", "--short"],
                text=True,
                capture_output=True,
                cwd=os.getcwd(),
                check=True,
            )
            changes = status_result.stdout.strip().splitlines()
            if not changes:
                return branch, "Clean working tree"
            staged = sum(1 for line in changes if line.startswith("A") or line.startswith("M") or line.startswith("R"))
            untracked = sum(1 for line in changes if line.startswith("??"))
            total = len(changes)
            summary = f"{total} change(s)" + (f", {staged} staged" if staged else "") + (f", {untracked} untracked" if untracked else "")
            return branch, summary
        except subprocess.CalledProcessError:
            return None, None

    def session_uptime(self) -> str:
        elapsed = int(time.monotonic() - self.session_start)
        minutes, seconds = divmod(elapsed, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours}h {minutes}m {seconds}s"
        return f"{minutes}m {seconds}s"

    def humanize_bytes(self, value: int) -> str:
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if value < 1024:
                return f"{value:.1f}{unit}"
            value /= 1024
        return f"{value:.1f}PB"

    def get_memory_summary(self) -> tuple[Optional[str], Optional[str]]:
        if shutil.which("ps") or platform.system() != "Windows":
            try:
                import psutil

                mem = psutil.virtual_memory()
                summary = f"{self.humanize_bytes(mem.used)} / {self.humanize_bytes(mem.total)} ({mem.percent:.0f}%)"
                bar = render_metric_bar(mem.percent, max_value=100.0)
                return summary, bar
            except (ImportError, Exception):
                return None, None
        return None, None

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
        directory_counts: Counter[str] = Counter()
        total_lines = 0
        todo_count = 0

        marker_names = {
            "pyproject.toml",
            "requirements.txt",
            "package.json",
            "tsconfig.json",
            "README.md",
            ".gitignore",
            "Dockerfile",
            "setup.cfg",
            "requirements.txt",
        }

        for dirpath, _, filenames in os.walk(root):
            relative_dir = os.path.relpath(dirpath, root)
            directory_counts[relative_dir] += len(filenames)
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
                if ext in {".py", ".js", ".ts", ".md", ".txt", ".json", ".yaml", ".yml"}:
                    try:
                        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                            lines = f.readlines()
                            total_lines += len(lines)
                            todo_count += sum(1 for line in lines if "TODO" in line or "FIXME" in line)
                    except OSError:
                        continue

        largest_files.sort(reverse=True)
        total_files = sum(extension_counts.values())
        top_types = sorted(extension_counts.items(), key=lambda item: item[1], reverse=True)[:6]
        top_dirs = directory_counts.most_common(4)

        project_type = "Mixed / unknown"
        if "package.json" in markers or "tsconfig.json" in markers:
            project_type = "Node.js / TypeScript"
        elif "pyproject.toml" in markers or "requirements.txt" in markers or any(ext == ".py" for ext in extension_counts):
            project_type = "Python"

        print(f"{ANSI_BOLD}Root:{ANSI_RESET} {root}")
        print(f"{ANSI_BOLD}Project Type:{ANSI_RESET} {project_type}")
        print(f"{ANSI_BOLD}Total files:{ANSI_RESET} {total_files}")
        print(f"{ANSI_BOLD}Total lines scanned:{ANSI_RESET} {total_lines}")
        print(f"{ANSI_BOLD}TODO/FIXME notes:{ANSI_RESET} {todo_count}")
        print(f"{ANSI_BOLD}Markers:{ANSI_RESET} {', '.join(sorted(markers)) or 'none'}")
        print()

        print(ANSI_CYAN + "Top file types:" + ANSI_RESET)
        for ext, count in top_types:
            print(f"  {ANSI_GREEN}{ext or '<none>'}{ANSI_RESET}: {count}")

        print()
        print(ANSI_CYAN + "Most active folders:" + ANSI_RESET)
        for folder, count in top_dirs:
            print(f"  {ANSI_BLUE}{folder}{ANSI_RESET}: {count} file(s)")

        print()
        print(ANSI_CYAN + "Largest files:" + ANSI_RESET)
        for size, relative in largest_files[:5]:
            print(f"  {ANSI_BLUE}{relative}{ANSI_RESET} — {size // 1024} KB")

        print()
        recommendations = []
        if project_type == "Python" and "README.md" not in markers:
            recommendations.append("Add README.md with a quick start section and sample commands.")
        if project_type == "Python" and "requirements.txt" not in markers and "pyproject.toml" not in markers:
            recommendations.append("Pin Python dependencies with requirements.txt or pyproject.toml.")
        if project_type == "Node.js / TypeScript" and "package.json" in markers:
            recommendations.append("Add npm scripts for lint, test, and build to simplify workflow.")
        if todo_count > 0:
            recommendations.append("Resolve or tag TODO/FIXME notes before the next release.")
        if total_lines > 0 and total_files > 0 and todo_count == 0:
            recommendations.append("The workspace looks clean — keep the momentum going!")
        if not markers:
            recommendations.append("Track the workspace with a README, .gitignore and project metadata files.")

        for recommendation in recommendations[:5]:
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

    async def show_version(self, argv: Sequence[str]) -> None:
        self.print_header("Version")
        print("Modern Workbench v1.0")
        print("Built with Python and asyncio.")
        print(f"Python version: {platform.python_version()}")

    async def smart_search(self, argv: Sequence[str]) -> None:
        """Perform intelligent search across files with context previews."""
        parser = argparse.ArgumentParser(prog="search", description="Smart file search with previews")
        parser.add_argument("query", help="Search query")
        parser.add_argument("--case", action="store_true", help="Case sensitive search")
        parser.add_argument("--regex", action="store_true", help="Treat query as regex")
        parser.add_argument("--type", help="File extension to search in (e.g., py, txt)")
        parser.add_argument("--preview", type=int, default=2, help="Lines of context around matches")

        try:
            args = parser.parse_args(argv)
        except SystemExit:
            return

        self.print_header("Smart Search Results")
        root = os.getcwd()
        query = args.query
        flags = 0 if args.case else re.IGNORECASE
        if args.regex:
            try:
                pattern = re.compile(query, flags)
            except re.error as e:
                print(f"{ANSI_RED}Invalid regex: {e}{ANSI_RESET}")
                return
        else:
            pattern = re.compile(re.escape(query), flags)

        matches = []
        for dirpath, _, filenames in os.walk(root):
            for filename in filenames:
                if args.type and not filename.endswith(f".{args.type}"):
                    continue
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines, 1):
                            if pattern.search(line):
                                start = max(0, i - args.preview - 1)
                                end = min(len(lines), i + args.preview)
                                context = lines[start:end]
                                matches.append({
                                    'file': os.path.relpath(filepath, root),
                                    'line': i,
                                    'match': line.strip(),
                                    'context': [l.strip() for l in context]
                                })
                except OSError:
                    continue

        if not matches:
            print("No matches found.")
            return

        shown = 0
        for match in matches:
            if shown >= 20:
                print(f"{ANSI_YELLOW}... and {len(matches) - 20} more matches{ANSI_RESET}")
                break
            print(f"{ANSI_BLUE}{match['file']}:{match['line']}{ANSI_RESET}")
            for j, ctx in enumerate(match['context']):
                line_num = match['line'] - args.preview + j
                if line_num == match['line']:
                    print(f"{ANSI_RED}{line_num:4d}: {ctx}{ANSI_RESET}")
                else:
                    print(f"{ANSI_DIM}{line_num:4d}: {ctx}{ANSI_RESET}")
            print()
            shown += 1

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
                minutes = remaining // 60
                seconds = remaining % 60
                time_str = f"{minutes:02d}:{seconds:02d}"
                print(f"{ANSI_BOLD}Focus:{ANSI_RESET} {bar} {time_str} remaining", end="\r", flush=True)
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
        grid = "   ".join([f"{ANSI_YELLOW}{step[:1]}{ANSI_RESET}:{ANSI_GREEN}{step[1:]}{ANSI_RESET}" for step in steps])
        print(render_centered(grid, width))
        print()
        print(ANSI_MAGENTA + wrap_text("This palette adapts to your terminal width and gives you an energizing flow for creative work.", width=width, indent=2) + ANSI_RESET)

    async def show_history(self, argv: Sequence[str]) -> None:
        self.print_header("Command History")
        if not self.history:
            print(ANSI_YELLOW + "No commands executed yet. Start with `status` or `idea`." + ANSI_RESET)
            return
        for index, record in enumerate(self.history, start=1):
            print(f"{ANSI_GREEN}{index:>2}.{ANSI_RESET} {record}")
        print()
        print(ANSI_DIM + "Tip: Enter 'secret' or 'magic' to reveal something unexpected." + ANSI_RESET)

    async def reveal_secret(self, argv: Sequence[str]) -> None:
        self.print_header("Secret Magic", style=ANSI_MAGENTA)
        print(rainbow_text("✨ HIDDEN FLOW UNLOCKED ✨"))
        print()
        hidden_lines = [
            "Your workspace is full of energy.",
            "A great idea is only one focused session away.",
            "Combine your momentum with structure and ship the best version first.",
        ]
        for line in hidden_lines:
            print(f"{ANSI_CYAN}{line}{ANSI_RESET}")
        print()
        print(ANSI_YELLOW + "You found the secret command! Keep exploring the palette for more surprises." + ANSI_RESET)

from __future__ import annotations

import argparse
import asyncio
import datetime
import difflib
import logging
import os
import platform
import random
import re
import shlex
import shutil
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
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
    ANSI_DIM,
    ANSI_GREEN,
    ANSI_MAGENTA,
    ANSI_RED,
    ANSI_RESET,
    ANSI_YELLOW,
    clear_screen,
    humanize_bytes,
    rainbow_text,
    render_centered,
    render_metric_bar,
    render_progress_bar,
    render_table,
    terminal_width,
    style_text,
    wrap_text,
)


class ModernWorkbench:
    """A modern terminal-based workbench for productivity and system management."""

    VERSION = "1.2"

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.commands: List[Command] = []
        self.history: List[str] = []
        self.session_start = time.monotonic()
        self.register_commands()

    def register_commands(self) -> None:
        palette = [
            Command(
                name="status",
                label="System Pulse",
                description="Show live system, environment and git metadata.",
                handler=self.show_system_pulse,
                aliases=("sys", "pulse", "info", "pulsecheck"),
                category="System",
            ),
            Command(
                name="workspace",
                label="Workspace Insight",
                description="Analyze project structure and recommend improvements.",
                handler=self.inspect_workspace,
                aliases=("inspect", "analyze", "audit", "radar"),
                category="System",
            ),
            Command(
                name="search",
                label="Smart Finder",
                description="Search files with preview, regex and extension filters.",
                handler=self.smart_search,
                aliases=("find", "grep", "seek"),
                category="System",
            ),
            Command(
                name="timer",
                label="Focus Timer",
                description="Run a countdown, Pomodoro session, or quick interval.",
                handler=self.run_focus_timer,
                aliases=("focus", "pomodoro", "pomo"),
                category="Flow",
            ),
            Command(
                name="boost",
                label="Momentum Booster",
                description="Generate a focused action plan and productivity prompt.",
                handler=self.generate_momentum_prompt,
                aliases=("mood", "hype", "charge"),
                category="Flow",
            ),
            Command(
                name="idea",
                label="Creative Spark",
                description="Create a fresh project idea or productivity blueprint.",
                handler=self.generate_innovation_prompt,
                aliases=("spark", "prompt"),
                category="Creative",
            ),
            Command(
                name="demo",
                label="Visual Flow",
                description="Render an adaptive, terminal-aware command palette preview.",
                handler=self.render_command_palette,
                aliases=("show", "view", "palette"),
                category="Creative",
            ),
            Command(
                name="history",
                label="Command History",
                description="Review the commands executed during this session.",
                handler=self.show_history,
                aliases=("log", "recent"),
                category="Utility",
            ),
            Command(
                name="shell",
                label="Shell Runner",
                description="Run a shell command and stream live output.",
                handler=self.run_shell_command,
                aliases=("run", "exec", "cmd"),
                category="Utility",
            ),
            Command(
                name="lint",
                label="Code Quality Check",
                description="Run linters like flake8 or pylint on the codebase.",
                handler=self.run_linter,
                aliases=("check", "quality"),
                category="Utility",
            ),
            Command(
                name="test",
                label="Run Tests",
                description="Execute test suites using pytest, unittest, or other test runners.",
                handler=self.run_tests,
                aliases=("tests", "unittest"),
                category="Utility",
            ),
            Command(
                name="secret",
                label="Secret Magic",
                description="Reveal a hidden easter egg and deeper workspace insight.",
                handler=self.reveal_secret,
                aliases=("magic", "easter", "hidden"),
                category="Creative",
                hidden=True,
            ),
        ]
        self.commands.extend(palette)

    def find_command(self, token: str) -> Optional[Command]:
        token = token.strip().lower()
        for command in self.commands:
            if command.matches(token):
                return command
        return None

    def find_command_by_prefix(self, token: str) -> Optional[Command]:
        normalized = token.strip().lower()
        candidates = [
            command
            for command in self.commands
            if command.name.startswith(normalized)
            or any(alias.startswith(normalized) for alias in command.aliases)
        ]
        return candidates[0] if len(candidates) == 1 else None

    def suggest_commands(self, token: str) -> List[str]:
        options = [command.name for command in self.commands if not command.hidden]
        return difflib.get_close_matches(token, options, n=4, cutoff=0.4)

    def readline_completer(self, text: str, state: int) -> Optional[str]:
        if readline is None:
            return None
        options = sorted({
            name
            for command in self.commands
            for name in (command.name, *command.aliases)
            if name.startswith(text)
        })
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
            "Type a command, use 'help' to open the palette, prefix with '!' for shell shortcuts, or explore hidden workflow features."
            " / ბრძანების შეყვანა, გამოიყენეთ 'help' პალიტრის დასახელებისთვის, დაابقე '!' shell მოკლე გზებისთვის."
        )

    async def run(self, args: argparse.Namespace) -> None:
        if args.run:
            command_name = args.run[0]
            argv = args.run[1:] + args.args
            await self.execute(command_name, argv)
            return

        clear_screen()
        self.setup_readline()
        self.print_welcome()
        await self.interactive_shell()

    async def execute(self, command_name: str, argv: Sequence[str] = ()) -> None:
        self.logger.info(f"Executing command: {command_name} with args: {argv}")
        command = self.find_command(command_name) or self.find_command_by_prefix(command_name)
        if command is None:
            self.print_header("Unknown command", style=ANSI_YELLOW)
            print(f"{ANSI_BOLD}{command_name}{ANSI_RESET} is not available.")
            suggestions = self.suggest_commands(command_name)
            if suggestions:
                print(f"Did you mean: {ANSI_GREEN}{', '.join(suggestions)}{ANSI_RESET}?")
            print("Type 'help' to open the command palette. / დაწერეთ 'help' პალიტრის გამოსარჩენად.")
            return

        self.history.append(" ".join([command_name, *list(argv)]).strip())
        await command.handler(argv)

    async def interactive_shell(self) -> None:
        while True:
            try:
                selection = input(f"{ANSI_BOLD}{ANSI_CYAN}> {ANSI_RESET}").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                print("Goodbye. Stay productive! ✨ / ნახვამდის. იყავით პროდუქტიული!")
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

            try:
                parts = shlex.split(selection)
            except ValueError:
                parts = selection.split()

            if parts:
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
        rows: list[list[str]] = []
        for command in sorted((cmd for cmd in self.commands if not cmd.hidden), key=lambda cmd: (cmd.category, cmd.name)):
            rows.append([
                command.category,
                command.name,
                ", ".join(command.aliases) if command.aliases else "-",
                command.description,
            ])
        print(render_table(rows, ["Category", "Command", "Aliases", "Description"]))
        print(f"{ANSI_BLUE}exit{ANSI_RESET}     Quit the workbench")
        print(f"{ANSI_BLUE}clear{ANSI_RESET}    Clear the screen")
        print()

    async def show_system_pulse(self, argv: Sequence[str]) -> None:
        self.print_header("System Pulse")
        metadata = self.collect_system_metadata()
        cpu_summary, memory_summary = self.collect_hardware_summary()
        branch, git_status = self.detect_git_status()

        self.print_section("Environment", metadata)
        if cpu_summary or memory_summary:
            self.print_section(
                "Hardware",
                {
                    "CPU": cpu_summary or "n/a",
                    "Memory": memory_summary or "n/a",
                },
            )

        if branch:
            print(f"{ANSI_BOLD}Git Branch:{ANSI_RESET} {branch}")
        if git_status:
            print(f"{ANSI_BOLD}Git Status:{ANSI_RESET} {git_status}")

        if branch or git_status:
            print()

        try:
            load_avg = os.getloadavg()
        except (AttributeError, OSError):
            load_avg = None

        if load_avg:
            print(f"{ANSI_BOLD}Load average:{ANSI_RESET} {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}")
            print(f"{render_metric_bar(load_avg[0], max_value=4.0)} {render_metric_bar(load_avg[1], max_value=4.0)} {render_metric_bar(load_avg[2], max_value=4.0)}")
            print()

        print(ANSI_DIM + "Tip: Use `workspace` to inspect your current folder or `search` to find code faster." + ANSI_RESET)

    def collect_system_metadata(self) -> dict[str, str]:
        root = Path.cwd()
        file_count = sum(1 for _ in root.rglob("*"))
        return {
            "Timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
            "Platform": platform.system(),
            "Release": platform.release(),
            "Architecture": platform.machine(),
            "Python": platform.python_version(),
            "Working Directory": str(root),
            "Session Uptime": self.session_uptime(),
            "Total Files": str(file_count),
        }

    def print_section(self, title: str, data: dict[str, str]) -> None:
        print(style_text(title, ANSI_CYAN, bold=True))
        for label, value in data.items():
            print(f"{ANSI_BOLD}{label:<18}{ANSI_RESET} {value}")
        print()

    def collect_hardware_summary(self) -> tuple[Optional[str], Optional[str]]:
        try:
            import psutil

            cpu = f"{psutil.cpu_percent(interval=0.2):.0f}% across {psutil.cpu_count(logical=True)} cores"
            cpu_mem = psutil.virtual_memory()
            memory = f"{humanize_bytes(cpu_mem.used)} / {humanize_bytes(cpu_mem.total)} ({cpu_mem.percent:.0f}%)"
            return cpu, memory
        except Exception:
            return None, None

    def detect_git_status(self) -> tuple[Optional[str], Optional[str]]:
        if shutil.which("git") is None:
            return None, None
        try:
            branch = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
                check=True,
            ).stdout.strip()
            status_lines = subprocess.run(
                ["git", "status", "--short"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
                check=True,
            ).stdout.strip().splitlines()
            if not status_lines:
                return branch, "Clean working tree"
            total = len(status_lines)
            staged = sum(1 for line in status_lines if line and line[0] != "?")
            untracked = sum(1 for line in status_lines if line.startswith("??"))
            summary = f"{total} change(s)"
            if staged:
                summary += f", {staged} staged"
            if untracked:
                summary += f", {untracked} untracked"
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

    async def stream_subprocess_output(self, stream: asyncio.StreamReader, prefix: str = "") -> None:
        while True:
            line = await stream.readline()
            if not line:
                break
            print(f"{prefix}{line.decode(errors='replace').rstrip()}{ANSI_RESET if prefix else ''}")

    async def run_shell_command(self, argv: Sequence[str]) -> None:
        self.print_header("Shell Runner")
        command_text = " ".join(argv) if argv else input("Shell command: ").strip()
        if not command_text:
            print(ANSI_YELLOW + "No shell command provided. Try `shell echo hello` or `!dir`. / არ არის shell ბრძანება. სცადეთ `shell echo hello` ან `!dir`." + ANSI_RESET)
            return

        print(ANSI_DIM + f"Executing:{ANSI_RESET} {command_text}")
        process = await asyncio.create_subprocess_shell(
            command_text,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        assert process.stdout is not None and process.stderr is not None
        await asyncio.gather(
            self.stream_subprocess_output(process.stdout),
            self.stream_subprocess_output(process.stderr, ANSI_RED),
        )
        return_code = await process.wait()
        print((ANSI_GREEN if return_code == 0 else ANSI_RED) + f"Process exited with code {return_code}." + ANSI_RESET)

    async def inspect_workspace(self, argv: Sequence[str]) -> None:
        self.print_header("Workspace Insight")
        root = Path.cwd()
        ext_counter: dict[str, int] = {}
        size_index: list[tuple[int, Path]] = []
        markers: set[str] = set()
        dir_counter: Counter[str] = Counter()
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
        }

        for item in root.rglob("*"):
            if item.is_dir():
                continue
            rel_dir = str(item.parent.relative_to(root)) if item.parent != root else "."
            dir_counter[rel_dir] += 1
            ext = item.suffix.lower() or "<none>"
            ext_counter[ext] = ext_counter.get(ext, 0) + 1
            try:
                size = item.stat().st_size
            except OSError:
                continue
            size_index.append((size, item))
            if item.name in marker_names:
                markers.add(item.name)
            if ext in {".py", ".js", ".ts", ".md", ".txt", ".json", ".yaml", ".yml"}:
                try:
                    text = item.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                lines = text.splitlines()
                total_lines += len(lines)
                todo_count += sum(1 for line in lines if "TODO" in line or "FIXME" in line)

        size_index.sort(reverse=True)
        top_ext = sorted(ext_counter.items(), key=lambda item: item[1], reverse=True)[:6]
        top_dirs = dir_counter.most_common(4)
        project_type = self.detect_project_type(markers, ext_counter)

        self.print_section(
            "Workspace Summary",
            {
                "Root": str(root),
                "Project Type": project_type,
                "Total files": str(sum(ext_counter.values())),
                "Total lines": str(total_lines),
                "TODO/FIXME notes": str(todo_count),
                "Markers": ", ".join(sorted(markers)) if markers else "none",
            },
        )

        print(ANSI_CYAN + "Top file types:" + ANSI_RESET)
        for ext, count in top_ext:
            print(f"  {ANSI_GREEN}{ext or '<none>'}{ANSI_RESET}: {count}")

        print()
        print(ANSI_CYAN + "Most active folders:" + ANSI_RESET)
        for folder, count in top_dirs:
            print(f"  {ANSI_BLUE}{folder}{ANSI_RESET}: {count} file(s)")

        print()
        print(ANSI_CYAN + "Largest files:" + ANSI_RESET)
        for size, item in size_index[:5]:
            print(f"  {ANSI_BLUE}{item.relative_to(root)}{ANSI_RESET} — {size // 1024} KB")

        print()
        for recommendation in self.workspace_recommendations(project_type, markers, todo_count):
            print(f"{ANSI_YELLOW}Tip:{ANSI_RESET} {recommendation}")

    def detect_project_type(self, markers: set[str], ext_counter: dict[str, int]) -> str:
        if "package.json" in markers or "tsconfig.json" in markers:
            return "Node.js / TypeScript"
        if "pyproject.toml" in markers or "requirements.txt" in markers or ext_counter.get(".py"):
            return "Python"
        return "Mixed / unknown"

    def workspace_recommendations(self, project_type: str, markers: set[str], todo_count: int) -> list[str]:
        recommendations: list[str] = []
        if project_type == "Python" and "README.md" not in markers:
            recommendations.append("Add README.md with a quick start section and sample commands.")
        if project_type == "Python" and "requirements.txt" not in markers and "pyproject.toml" not in markers:
            recommendations.append("Pin Python dependencies with requirements.txt or pyproject.toml.")
        if project_type == "Node.js / TypeScript" and "package.json" in markers:
            recommendations.append("Add npm scripts for lint, test, and build to simplify workflow.")
        if todo_count > 0:
            recommendations.append("Resolve or tag TODO/FIXME notes before the next release.")
        if todo_count == 0:
            recommendations.append("The workspace looks clean — keep the momentum going!")
        if not markers:
            recommendations.append("Track the workspace with a README, .gitignore and project metadata files.")
        return recommendations[:5]

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
        print(f"Modern Workbench v{self.VERSION}")
        print("Built with Python and asyncio.")
        print(f"Python version: {platform.python_version()}")
        print(f"Runtime: {platform.python_implementation()} on {platform.system()} {platform.release()}")

    async def run_linter(self, argv: Sequence[str]) -> None:
        self.print_header("Code Quality Check")
        linters = ["flake8", "pylint", "black --check", "isort --check-only"]
        available_linters = []
        for linter in linters:
            cmd = linter.split()[0]
            if shutil.which(cmd):
                available_linters.append(linter)

        if not available_linters:
            print(ANSI_YELLOW + "No linters found. Install flake8, pylint, black, or isort for code quality checks." + ANSI_RESET)
            return

        print(f"Available linters: {', '.join(available_linters)}")
        print("Running checks...")
        for linter in available_linters:
            print(f"\n{ANSI_CYAN}Running {linter}:{ANSI_RESET}")
            try:
                process = await asyncio.create_subprocess_shell(
                    linter,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=Path.cwd(),
                )
                stdout, stderr = await process.communicate()
                if stdout:
                    print(stdout.decode(errors='replace'))
                if stderr:
                    print(ANSI_RED + stderr.decode(errors='replace') + ANSI_RESET)
                if process.returncode == 0:
                    print(ANSI_GREEN + f"{linter} passed." + ANSI_RESET)
                else:
                    print(ANSI_YELLOW + f"{linter} found issues (exit code {process.returncode})." + ANSI_RESET)
            except Exception as e:
                print(ANSI_RED + f"Error running {linter}: {e}" + ANSI_RESET)

    async def run_tests(self, argv: Sequence[str]) -> None:
        self.print_header("Run Tests")
        test_runners = ["pytest", "python -m unittest discover", "python -m pytest"]
        available_runners = []
        for runner in test_runners:
            cmd = runner.split()[0]
            if shutil.which(cmd):
                available_runners.append(runner)

        if not available_runners:
            print(ANSI_YELLOW + "No test runners found. Install pytest or use unittest for testing." + ANSI_RESET)
            return

        print(f"Available test runners: {', '.join(available_runners)}")
        print("Running tests...")
        for runner in available_runners[:1]:  # Run only the first available to avoid duplicates
            print(f"\n{ANSI_CYAN}Running {runner}:{ANSI_RESET}")
            try:
                process = await asyncio.create_subprocess_shell(
                    runner,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=Path.cwd(),
                )
                stdout, stderr = await process.communicate()
                if stdout:
                    print(stdout.decode(errors='replace'))
                if stderr:
                    print(ANSI_RED + stderr.decode(errors='replace') + ANSI_RESET)
                if process.returncode == 0:
                    print(ANSI_GREEN + f"Tests passed with {runner}." + ANSI_RESET)
                else:
                    print(ANSI_YELLOW + f"Tests failed with {runner} (exit code {process.returncode})." + ANSI_RESET)
            except Exception as e:
                print(ANSI_RED + f"Error running {runner}: {e}" + ANSI_RESET)

    async def smart_search(self, argv: Sequence[str]) -> None:
        parser.add_argument("query", help="Search query")
        parser.add_argument("--case", action="store_true", help="Case sensitive search")
        parser.add_argument("--regex", action="store_true", help="Treat query as regex")
        parser.add_argument("--type", help="File extension to search in (e.g., py, txt)")
        parser.add_argument("--preview", type=int, default=2, help="Lines of context around matches")
        parser.add_argument("--max", type=int, default=20, help="Maximum number of results to display")
        parser.add_argument("--path", default=".", help="Path to search from")

        try:
            args = parser.parse_args(argv)
        except SystemExit:
            return

        self.print_header("Smart Search Results")
        root = Path(args.path).resolve()
        flags = 0 if args.case else re.IGNORECASE
        if args.regex:
            try:
                pattern = re.compile(args.query, flags)
            except re.error as exc:
                print(f"{ANSI_RED}Invalid regex: {exc}{ANSI_RESET}")
                return
        else:
            pattern = re.compile(re.escape(args.query), flags)

        matches: list[dict[str, object]] = []
        for filepath in root.rglob("*"):
            if filepath.is_dir():
                continue
            if args.type and filepath.suffix.lower() != f".{args.type.lower()}":
                continue
            try:
                text = filepath.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            lines = text.splitlines()
            for line_number, line in enumerate(lines, start=1):
                if pattern.search(line):
                    start = max(0, line_number - args.preview - 1)
                    end = min(len(lines), line_number + args.preview)
                    context = lines[start:end]
                    matches.append(
                        {
                            "file": str(filepath.relative_to(root)),
                            "line": line_number,
                            "match": line.strip(),
                            "context": context,
                        }
                    )
                    if len(matches) >= args.max * 2:
                        break
            if len(matches) >= args.max * 2:
                break

        if not matches:
            print("No matches found.")
            return

        for match in matches[: args.max]:
            print(f"{ANSI_BLUE}{match['file']}:{match['line']}{ANSI_RESET}")
            for offset, line_text in enumerate(match["context"], start=1):
                line_num = match["line"] - args.preview + offset - 1
                marker = ANSI_RED if line_num == match["line"] else ANSI_DIM
                print(f"{marker}{line_num:4d}:{ANSI_RESET} {line_text}")
            print()

        if len(matches) > args.max:
            print(f"{ANSI_YELLOW}... and {len(matches) - args.max} more results{ANSI_RESET}")

    async def generate_innovation_prompt(self, argv: Sequence[str]) -> None:
        self.print_header("Creative Spark")
        themes = [
            {
                "title": "Terminal Zen",
                "idea": "Build a distraction-free CLI that rewards progress with ambient animations and smart goal nudges.",
                "steps": [
                    "Map daily habits to tiny terminal badges.",
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
        print(ANSI_YELLOW + "Tip:" + ANSI_RESET + " Use `idea` again to generate a new spark." + ANSI_RESET)

    async def run_focus_timer(self, argv: Sequence[str]) -> None:
        self.print_header("Focus Timer")
        duration_minutes = 25
        cycles = 1
        if argv:
            first = argv[0].lower()
            if first.isdigit():
                duration_minutes = max(1, min(180, int(first)))
            elif first in {"short", "quick", "tiny"}:
                duration_minutes = 5
            elif first in {"focus", "work", "pomodoro", "pomo"}:
                duration_minutes = 25
        if len(argv) > 1 and argv[1].isdigit():
            cycles = max(1, min(8, int(argv[1])))

        total_seconds = duration_minutes * 60
        print(f"{ANSI_MAGENTA}Session:{ANSI_RESET} {duration_minutes} minutes × {cycles} cycle(s)")
        for cycle in range(1, cycles + 1):
            print(f"{ANSI_BLUE}Cycle {cycle}/{cycles}{ANSI_RESET}")
            start = time.monotonic()
            while True:
                elapsed = int(time.monotonic() - start)
                if elapsed >= total_seconds:
                    break
                remaining = total_seconds - elapsed
                bar = render_progress_bar(elapsed / total_seconds, length=32)
                print(
                    f"{ANSI_BOLD}Focus:{ANSI_RESET} {bar} {remaining // 60:02d}:{remaining % 60:02d} remaining",
                    end="\r",
                    flush=True,
                )
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
        print(render_centered("  ".join(f"{ANSI_CYAN}[ {step} ]{ANSI_RESET}" for step in steps), width))
        print()
        print(render_centered(rainbow_text("THE MOST MODERN COMMAND HUB"), width))
        print()
        print(render_centered("   ".join(f"{ANSI_YELLOW}{step[:1]}{ANSI_RESET}:{ANSI_GREEN}{step[1:]}{ANSI_RESET}" for step in steps), width))
        print()
        print(ANSI_MAGENTA + wrap_text("This palette adapts to your terminal width and gives you an energizing flow for creative work.", width=width, indent=2) + ANSI_RESET)

    async def show_history(self, argv: Sequence[str]) -> None:
        self.print_header("Command History")
        if not self.history:
            print(ANSI_YELLOW + "No commands executed yet. Start with `status` or `idea`. / ჯერ არ დაგიდენიათ ბრძანება. დაიწყეთ `status` ან `idea`." + ANSI_RESET)
            return
        recent = self.history[-20:]
        for index, record in enumerate(recent, start=max(1, len(self.history) - len(recent) + 1)):
            print(f"{ANSI_GREEN}{index:>2}.{ANSI_RESET} {record}")
        print()
        print(ANSI_DIM + "Tip: Enter 'secret' or 'magic' to reveal something unexpected." + ANSI_RESET)

    async def reveal_secret(self, argv: Sequence[str]) -> None:
        self.print_header("Secret Magic", style=ANSI_MAGENTA)
        print(rainbow_text("✨ HIDDEN FLOW UNLOCKED ✨"))
        print()
        for message in [
            "Your workspace is full of energy.",
            "A great idea is only one focused session away.",
            "Combine your momentum with structure and ship the best version first.",
        ]:
            print(f"{ANSI_CYAN}{message}{ANSI_RESET}")
        print()
        print(ANSI_YELLOW + "You found the secret command! Keep exploring the palette for more surprises." + ANSI_RESET)

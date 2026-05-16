from __future__ import annotations

import argparse
import asyncio
import difflib
import importlib
import logging
import shlex
import sys
import time
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
        self.commands.extend(self.load_component_commands())
        self.commands.append(
            Command(
                name="help",
                label="Command Help",
                description="Show available commands and usage help.",
                handler=show_help,
                aliases=("menu", "list"),
                category="Utility",
            )
        )

    def load_component_commands(self) -> list[Command]:
        component_dir = Path(__file__).parent / "components"
        commands: list[Command] = []
        if not component_dir.exists():
            return commands

        for path in sorted(component_dir.glob("*.py")):
            if path.name.startswith("_"):
                continue
            module_name = f"components.{path.stem}"
            try:
                module = importlib.import_module(module_name)
            except Exception as exc:
                self.logger.error(f"Failed to load component {module_name}: {exc}")
                continue

            get_commands = getattr(module, "get_commands", None)
            if callable(get_commands):
                try:
                    commands.extend(get_commands(self))
                except Exception as exc:
                    self.logger.error(f"Component {module_name} failed to register commands: {exc}")
        return commands

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
        await command.handler(self, argv)

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


async def show_help(workbench, argv: Sequence[str]) -> None:
    workbench.print_header("Help")
    workbench.print_menu()

    async def show_help(self, argv: Sequence[str]) -> None:
        self.print_header("Help")
        self.print_menu()

    def print_section(self, title: str, data: dict[str, str]) -> None:
        print(style_text(title, ANSI_CYAN, bold=True))
        for label, value in data.items():
            print(f"{ANSI_BOLD}{label:<18}{ANSI_RESET} {value}")
        print()

from __future__ import annotations

import asyncio
import platform
import shutil
import subprocess
from pathlib import Path

from commands import Command, command
from terminal import ANSI_BLUE, ANSI_CYAN, ANSI_DIM, ANSI_GREEN, ANSI_RED, ANSI_RESET, ANSI_YELLOW


async def stream_subprocess_output(stream: asyncio.StreamReader, prefix: str = "") -> None:
    while True:
        line = await stream.readline()
        if not line:
            break
        print(f"{prefix}{line.decode(errors='replace').rstrip()}{ANSI_RESET if prefix else ''}")


@command(
    name="shell",
    label="Shell Runner",
    description="Run shell commands with output streaming.",
    aliases=("sh", "run", "!"),
    category="Utility",
)
async def run_shell_command(workbench, argv) -> None:
    workbench.print_header("Shell Runner")
    command_text = " ".join(argv) if argv else input("Shell command: ").strip()
    if not command_text:
        print(
            ANSI_YELLOW
            + "No shell command provided. Try `shell echo hello` or `!dir`."
            + ANSI_RESET
        )
        return

    print(ANSI_DIM + f"Executing:{ANSI_RESET} {command_text}")
    process = await asyncio.create_subprocess_shell(
        command_text,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    assert process.stdout is not None and process.stderr is not None
    await asyncio.gather(
        stream_subprocess_output(process.stdout),
        stream_subprocess_output(process.stderr, ANSI_RED),
    )
    return_code = await process.wait()
    print((ANSI_GREEN if return_code == 0 else ANSI_RED) + f"Process exited with code {return_code}." + ANSI_RESET)


@command(
    name="history",
    label="Execution History",
    description="Review command execution history.",
    aliases=("log", "past"),
    category="Utility",
)
async def show_history(workbench, argv) -> None:
    workbench.print_header("Command History")
    if not workbench.history:
        print(
            ANSI_YELLOW
            + "No commands executed yet. Start with `status` or `idea`."
            + ANSI_RESET
        )
        return

    recent = workbench.history[-20:]
    for index, record in enumerate(recent, start=max(1, len(workbench.history) - len(recent) + 1)):
        print(f"{ANSI_GREEN}{index:>2}.{ANSI_RESET} {record}")
    print()
    print(ANSI_DIM + "Tip: Enter 'secret' or 'magic' to reveal something unexpected." + ANSI_RESET)


@command(
    name="lint",
    label="Code Quality",
    description="Run code quality checks (flake8, pylint, black, etc.).",
    aliases=("check", "quality", "format"),
    category="Utility",
)
async def run_linter(workbench, argv) -> None:
    workbench.print_header("Code Quality Check")
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


@command(
    name="test",
    label="Test Suite",
    description="Execute test suites (pytest, unittest).",
    aliases=("verify", "unit"),
    category="Utility",
)
async def run_tests(workbench, argv) -> None:
    workbench.print_header("Test Execution")
    test_runners = ["pytest", "python -m unittest discover"]
    runner = None
    for r in test_runners:
        cmd = r.split()[0]
        if shutil.which(cmd):
            runner = r
            break

    if not runner:
        print(ANSI_YELLOW + "No test runner found. Install pytest to run tests." + ANSI_RESET)
        return

    print(f"Running tests with {runner}...")
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
            print(ANSI_GREEN + "All tests passed." + ANSI_RESET)
        else:
            print(ANSI_RED + f"Tests failed with exit code {process.returncode}." + ANSI_RESET)
    except Exception as e:
        print(ANSI_RED + f"Error running tests: {e}" + ANSI_RESET)


@command(
    name="version",
    label="Version Info",
    description="Show workbench version and runtime info.",
    aliases=("v", "info"),
    category="Utility",
)
async def show_version(workbench, argv) -> None:
    workbench.print_header("Workbench Version")
    data = {
        "Version": workbench.VERSION,
        "Python": platform.python_version(),
        "OS": platform.system(),
        "CWD": str(Path.cwd()),
    }
    workbench.print_section("Runtime Information", data)

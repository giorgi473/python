from __future__ import annotations

import asyncio
import platform
import shutil
import subprocess
from pathlib import Path

from commands import Command
from terminal import ANSI_BLUE, ANSI_CYAN, ANSI_DIM, ANSI_GREEN, ANSI_RED, ANSI_RESET, ANSI_YELLOW


async def stream_subprocess_output(stream: asyncio.StreamReader, prefix: str = "") -> None:
    while True:
        line = await stream.readline()
        if not line:
            break
        print(f"{prefix}{line.decode(errors='replace').rstrip()}{ANSI_RESET if prefix else ''}")


async def run_shell_command(workbench, argv) -> None:
    workbench.print_header("Shell Runner")
    command_text = " ".join(argv) if argv else input("Shell command: ").strip()
    if not command_text:
        print(
            ANSI_YELLOW
            + "No shell command provided. Try `shell echo hello` or `!dir`. / არ არის shell ბრძანება. სცადეთ `shell echo hello` ან `!dir`."
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


async def show_history(workbench, argv) -> None:
    workbench.print_header("Command History")
    if not workbench.history:
        print(
            ANSI_YELLOW
            + "No commands executed yet. Start with `status` or `idea`. / ჯერ არა გაქვთ ბრძანება. დაიწყეთ `status` ან `idea`."
            + ANSI_RESET
        )
        return

    recent = workbench.history[-20:]
    for index, record in enumerate(recent, start=max(1, len(workbench.history) - len(recent) + 1)):
        print(f"{ANSI_GREEN}{index:>2}.{ANSI_RESET} {record}")
    print()
    print(ANSI_DIM + "Tip: Enter 'secret' or 'magic' to reveal something unexpected." + ANSI_RESET)


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


async def run_tests(workbench, argv) -> None:
    workbench.print_header("Run Tests")
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
    for runner in available_runners[:1]:
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


async def show_version(workbench, argv) -> None:
    workbench.print_header("Version")
    print(f"Modern Workbench v{workbench.VERSION}")
    print("Built with Python and asyncio.")
    print(f"Python version: {platform.python_version()}")
    print(f"Runtime: {platform.python_implementation()} on {platform.system()} {platform.release()}")


def get_commands(workbench) -> list[Command]:
    return [
        Command(
            name="history",
            label="Command History",
            description="Review the commands executed during this session.",
            handler=show_history,
            aliases=("log", "recent"),
            category="Utility",
        ),
        Command(
            name="shell",
            label="Shell Runner",
            description="Run a shell command and stream live output.",
            handler=run_shell_command,
            aliases=("run", "exec", "cmd"),
            category="Utility",
        ),
        Command(
            name="version",
            label="Workbench Version",
            description="Show version and runtime details.",
            handler=show_version,
            aliases=("ver", "about"),
            category="Utility",
        ),
        Command(
            name="lint",
            label="Code Quality Check",
            description="Run linters like flake8 or pylint on the codebase.",
            handler=run_linter,
            aliases=("check", "quality"),
            category="Utility",
        ),
        Command(
            name="test",
            label="Run Tests",
            description="Execute test suites using pytest, unittest, or other test runners.",
            handler=run_tests,
            aliases=("tests", "unittest"),
            category="Utility",
        ),
    ]

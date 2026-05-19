from __future__ import annotations

import datetime
import os
import platform
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional

from commands import Command, command
from terminal import (
    ANSI_BOLD,
    ANSI_CYAN,
    ANSI_DIM,
    ANSI_GREEN,
    ANSI_MAGENTA,
    ANSI_RED,
    ANSI_RESET,
    render_metric_bar,
    wrap_text,
    humanize_bytes,
)


@command(
    name="status",
    label="System Pulse",
    description="Show system pulse, environment, and git metadata.",
    aliases=("sys", "pulse"),
    category="System",
)
async def show_system_pulse(workbench, argv) -> None:
    workbench.print_header("System Pulse")
    metadata = collect_system_metadata(workbench.session_start)
    cpu_summary, memory_summary = collect_hardware_summary()
    branch, git_status = detect_git_status()

    workbench.print_section("Environment", metadata)
    if cpu_summary or memory_summary:
        workbench.print_section(
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
        print(
            f"{ANSI_BOLD}Load average:{ANSI_RESET} {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}"
        )
        print(
            f"{render_metric_bar(load_avg[0], max_value=4.0)} "
            f"{render_metric_bar(load_avg[1], max_value=4.0)} "
            f"{render_metric_bar(load_avg[2], max_value=4.0)}"
        )
        print()

    print(
        ANSI_DIM
        + "Tip: Use `workspace` to inspect your current folder or `search` to find code faster."
        + ANSI_RESET
    )


def collect_system_metadata(start_time: float) -> dict[str, str]:
    root = Path.cwd()
    file_count = sum(1 for _ in root.rglob("*"))
    return {
        "Timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "Platform": platform.system(),
        "Release": platform.release(),
        "Architecture": platform.machine(),
        "Python": platform.python_version(),
        "Working Directory": str(root),
        "Session Uptime": session_uptime(start_time),
        "Total Files": str(file_count),
    }


def collect_hardware_summary() -> tuple[Optional[str], Optional[str]]:
    try:
        import psutil

        cpu = f"{psutil.cpu_percent(interval=0.2):.0f}% across {psutil.cpu_count(logical=True)} cores"
        cpu_mem = psutil.virtual_memory()
        memory = f"{humanize_bytes(cpu_mem.used)} / {humanize_bytes(cpu_mem.total)} ({cpu_mem.percent:.0f}%)"
        return cpu, memory
    except Exception:
        return None, None


def detect_git_status() -> tuple[Optional[str], Optional[str]]:
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


def session_uptime(start_time: float) -> str:
    elapsed = int(time.monotonic() - start_time)
    minutes, seconds = divmod(elapsed, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m {seconds}s"
    return f"{minutes}m {seconds}s"

from __future__ import annotations

import asyncio
import random
import time

from commands import Command
from terminal import ANSI_BOLD, ANSI_CYAN, ANSI_GREEN, ANSI_MAGENTA, ANSI_YELLOW, render_progress_bar


async def generate_momentum_prompt(workbench, argv) -> None:
    workbench.print_header("Momentum Booster")
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


async def run_focus_timer(workbench, argv) -> None:
    workbench.print_header("Focus Timer")
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


def get_commands(workbench) -> list[Command]:
    return [
        Command(
            name="timer",
            label="Focus Timer",
            description="Run a countdown, Pomodoro session, or quick interval.",
            handler=run_focus_timer,
            aliases=("focus", "pomodoro", "pomo"),
            category="Flow",
        ),
        Command(
            name="boost",
            label="Momentum Booster",
            description="Generate a focused action plan and productivity prompt.",
            handler=generate_momentum_prompt,
            aliases=("mood", "hype", "charge"),
            category="Flow",
        ),
    ]

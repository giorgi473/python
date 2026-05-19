from __future__ import annotations

import random

from commands import Command
from terminal import (
    ANSI_BOLD, ANSI_CYAN, ANSI_GREEN, ANSI_MAGENTA, ANSI_RESET, ANSI_YELLOW, 
    render_centered, rainbow_text, wrap_text, terminal_width,
    RGB, gradient_text, render_box, Style
)


async def generate_innovation_prompt(workbench, argv) -> None:
    workbench.print_header("Creative Spark")
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
    
    # Use gradient for title
    title = gradient_text(choice["title"], RGB(255, 100, 0), RGB(255, 255, 0))
    
    # Use render_box for the idea
    idea_content = f"{choice['idea']}\n\n" + "\n".join(f"• {step}" for step in choice["steps"])
    print(render_box(idea_content, title=choice["title"], color=ANSI_CYAN))
    
    print()
    print(Style().dim().italic().apply(f"Tip: Use `idea` again to generate a new spark."))


async def render_command_palette(workbench, argv) -> None:
    workbench.print_header("Visual Flow")
    width = terminal_width()
    steps = ["Spark", "Sketch", "Focus", "Ship"]
    
    # Use Fluent API for steps
    styled_steps = "  ".join(Style().color(ANSI_CYAN).bold().apply(f"[ {step} ]") for step in steps)
    print(render_centered(styled_steps, width))
    
    print()
    # Use Gradient for the main title
    main_title = gradient_text("THE MOST MODERN COMMAND HUB", RGB(0, 255, 255), RGB(255, 0, 255))
    print(render_centered(main_title, width))
    
    print()
    shortcuts = "   ".join(f"{ANSI_YELLOW}{step[:1]}{ANSI_RESET}:{ANSI_GREEN}{step[1:]}{ANSI_RESET}" for step in steps)
    print(render_centered(shortcuts, width))
    
    print()
    palette_desc = "This palette adapts to your terminal width and gives you an energizing flow for creative work."
    print(render_centered(Style().color(ANSI_MAGENTA).italic().apply(palette_desc), width))


async def reveal_secret(workbench, argv) -> None:
    workbench.print_header("Secret Magic", style=ANSI_MAGENTA)
    
    # Advanced gradient
    secret_title = gradient_text("✨ HIDDEN FLOW UNLOCKED ✨", RGB(255, 255, 255), RGB(255, 0, 150))
    print(render_centered(secret_title))
    print()
    
    messages = [
        "Your workspace is full of energy.",
        "A great idea is only one focused session away.",
        "Combine your momentum with structure and ship the best version first.",
    ]
    
    for message in messages:
        print(render_centered(Style().color(ANSI_CYAN).apply(message)))
    
    print()
    tip = "You found the secret command! Keep exploring the palette for more surprises."
    print(render_centered(Style().color(ANSI_YELLOW).dim().apply(tip)))


def get_commands(workbench) -> list[Command]:
    return [
        Command(
            name="idea",
            label="Creative Spark",
            description="Create a fresh project idea or productivity blueprint.",
            handler=generate_innovation_prompt,
            aliases=("spark", "prompt"),
            category="Creative",
        ),
        Command(
            name="demo",
            label="Visual Flow",
            description="Render an adaptive, terminal-aware command palette preview.",
            handler=render_command_palette,
            aliases=("show", "view", "palette"),
            category="Creative",
        ),
        Command(
            name="secret",
            label="Secret Magic",
            description="Reveal a hidden easter egg and deeper workspace insight.",
            handler=reveal_secret,
            aliases=("magic", "easter", "hidden"),
            category="Creative",
            hidden=True,
        ),
    ]

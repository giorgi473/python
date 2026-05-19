from __future__ import annotations

import os
import re
from collections import Counter
from pathlib import Path
from typing import Set, List

from commands import Command, command
from terminal import ANSI_BLUE, ANSI_CYAN, ANSI_GREEN, ANSI_YELLOW, ANSI_RESET


@command(
    name="workspace",
    label="Workspace Insight",
    description="Analyze project structure and recommend improvements.",
    aliases=("inspect", "analyze", "audit", "radar"),
    category="System",
)
async def inspect_workspace(workbench, argv) -> None:
    workbench.print_header("Workspace Insight")
    root = Path.cwd()
    ext_counter: dict[str, int] = {}
    size_index: list[tuple[int, Path]] = []
    markers: Set[str] = set()
    dir_counter: Counter[str] = Counter()
    total_lines = 0
    todo_count = 0
    
    # Performance Optimization: Exclude common large/noise directories
    exclude_dirs = {".git", "__pycache__", "node_modules", ".venv", "venv", ".pytest_cache", ".mypy_cache"}
    
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

    # Improved file traversal with exclusion logic
    for path, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        current_path = Path(path)
        rel_dir = str(current_path.relative_to(root)) if current_path != root else "."
        
        for file in files:
            item = current_path / file
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
                    # Limit reading large files for TODO search
                    if size < 1024 * 1024: # 1MB limit
                        text = item.read_text(encoding="utf-8", errors="ignore")
                        lines = text.splitlines()
                        total_lines += len(lines)
                        todo_count += sum(1 for line in lines if "TODO" in line or "FIXME" in line)
                except OSError:
                    continue

    size_index.sort(reverse=True)
    top_ext = sorted(ext_counter.items(), key=lambda item: item[1], reverse=True)[:6]
    top_dirs = dir_counter.most_common(4)
    project_type = detect_project_type(markers, ext_counter)

    workbench.print_section(
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
    for recommendation in workspace_recommendations(project_type, markers, todo_count):
        print(f"{ANSI_YELLOW}Tip:{ANSI_RESET} {recommendation}")


def detect_project_type(markers: Set[str], ext_counter: dict[str, int]) -> str:
    if "package.json" in markers or "tsconfig.json" in markers:
        return "Node.js / TypeScript"
    if "pyproject.toml" in markers or "requirements.txt" in markers or ext_counter.get(".py"):
        return "Python"
    return "Mixed / unknown"


def workspace_recommendations(project_type: str, markers: Set[str], todo_count: int) -> list[str]:
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

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

from commands import Command, command
from terminal import ANSI_BLUE, ANSI_CYAN, ANSI_DIM, ANSI_RED, ANSI_RESET, ANSI_YELLOW


@command(
    name="search",
    label="Smart Finder",
    description="Search files with preview, regex and extension filters.",
    aliases=("find", "grep", "seek"),
    category="System",
)
async def smart_search(workbench, argv) -> None:
    parser = argparse.ArgumentParser(description="Search files in the workspace with regex and preview.")
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

    workbench.print_header("Smart Search Results")
    root = Path(args.path).resolve()
    
    # Performance Optimization: Exclude common large/noise directories
    exclude_dirs = {".git", "__pycache__", "node_modules", ".venv", "venv", ".pytest_cache", ".mypy_cache"}
    
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
    
    # Improved traversal with exclusion logic
    for path, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        current_path = Path(path)
        
        for file in files:
            filepath = current_path / file
            
            if args.type and filepath.suffix.lower() != f".{args.type.lower()}":
                continue
            
            try:
                # Performance: Skip files larger than 1MB for searching
                if filepath.stat().st_size > 1024 * 1024:
                    continue
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

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio

from workbench import ModernWorkbench


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(description="Modern terminal workbench with async functionality.")
    parser.add_argument("--version", action="version", version="Modern Workbench 1.2")
    parser.add_argument(
        "--run",
        help="Run a single command without starting the interactive shell.",
    )
    return parser.parse_known_args()


def main() -> None:
    args, unknown = parse_args()
    workbench = ModernWorkbench()
    try:
        if args.run:
            # Reconstruct argv for the command execution
            # We treat args.run as the command name and unknown as its arguments
            asyncio.run(workbench.execute(args.run, unknown))
        else:
            asyncio.run(workbench.run(args))
    except KeyboardInterrupt:
        print("\nInterrupted. See you soon!")


if __name__ == "__main__":
    main()

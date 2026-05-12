#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio

from workbench import ModernWorkbench


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Modern terminal workbench with async functionality.")
    parser.add_argument("--version", action="version", version="Modern Workbench 1.2")
    parser.add_argument(
        "--run",
        nargs="*",
        default=[],
        help="Run a single command and optional arguments without starting the interactive shell.",
    )
    parser.add_argument(
        "--args",
        "-a",
        nargs="*",
        default=[],
        help="Additional arguments passed to the command when --run is used.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    workbench = ModernWorkbench()
    try:
        asyncio.run(workbench.run(args))
    except KeyboardInterrupt:
        print("\nInterrupted. See you soon!")


if __name__ == "__main__":
    main()

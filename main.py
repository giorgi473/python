#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio

from workbench import ModernWorkbench


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Modern terminal workbench with async functionality.")
    parser.add_argument("--command", "-c", help="Run a single command without the interactive shell.")
    parser.add_argument("--args", "-a", nargs="*", default=[], help="Arguments to pass to the selected command.")
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

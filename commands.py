from __future__ import annotations

from dataclasses import dataclass
from typing import Awaitable, Callable, Sequence


@dataclass(frozen=True)
class Command:
    name: str
    label: str
    description: str
    handler: Callable[["ModernWorkbench", Sequence[str]], Awaitable[None]]
    aliases: Sequence[str] = ()
    hidden: bool = False

    def matches(self, token: str) -> bool:
        target = token.lower()
        return target == self.name or target in (alias.lower() for alias in self.aliases)

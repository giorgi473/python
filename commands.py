from __future__ import annotations

from dataclasses import dataclass, field
from typing import Awaitable, Callable, Sequence

__all__ = ["Command"]


@dataclass(frozen=True, slots=True)
class Command:
    """Represents a command in the workbench."""
    name: str
    label: str
    description: str
    handler: Callable[["ModernWorkbench", Sequence[str]], Awaitable[None]]
    aliases: Sequence[str] = field(default_factory=tuple)
    category: str = "General"
    hidden: bool = False

    def matches(self, token: str) -> bool:
        """Check if the token matches this command's name or aliases."""
        target = token.lower()
        return target == self.name.lower() or any(target == alias.lower() for alias in self.aliases)

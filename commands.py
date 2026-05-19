from __future__ import annotations

import functools
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Sequence, TypeVar, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from workbench import ModernWorkbench

__all__ = ["Command", "command"]

F = TypeVar("F", bound=Callable[..., Awaitable[None]])

@dataclass(frozen=True, slots=True)
class Command:
    """Represents a command in the workbench."""
    name: str
    label: str
    description: str
    handler: Callable[[ModernWorkbench, Sequence[str]], Awaitable[None]]
    aliases: Sequence[str] = field(default_factory=tuple)
    category: str = "General"
    hidden: bool = False

    def matches(self, token: str) -> bool:
        """Check if the token matches this command's name or aliases."""
        target = token.lower()
        return target == self.name.lower() or any(target == alias.lower() for alias in self.aliases)


def command(
    name: str,
    label: str,
    description: str,
    aliases: Sequence[str] = (),
    category: str = "General",
    hidden: bool = False,
):
    """Decorator to mark a function as a workbench command."""
    def decorator(func: F) -> F:
        func._command_metadata = {
            "name": name,
            "label": label,
            "description": description,
            "aliases": aliases,
            "category": category,
            "hidden": hidden,
        }
        return func
    return decorator

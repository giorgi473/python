from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
import asyncio


@dataclass(frozen=True)
class Command:
    name: str
    label: str
    description: str
    handler: Callable[[], asyncio.Future[None]]

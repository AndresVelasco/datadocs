from __future__ import annotations

from typing import Any, Protocol


class Source(Protocol):
    def load_data(self) -> Any:
        ...


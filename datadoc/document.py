from __future__ import annotations

from pathlib import Path
from typing import Any

from datadoc.exceptions import ConfigurationError
from datadoc.render import render
from datadoc.sources.protocol import Source


class Document:
    def __init__(
        self,
        *,
        template_path: str,
        data: Any | None = None,
        source: Source | None = None,
        params: dict[str, Any] | None = None,
    ) -> None:
        if data is not None and source is not None:
            raise ConfigurationError(
                "Document accepts either data or source, never both."
            )
        if data is None and source is None:
            raise ConfigurationError("Document requires either data or source.")

        self.template_path = template_path
        self.data = data
        self.source = source
        self.params = params or {}

    def render(self) -> str:
        data = self.source.load_data() if self.source is not None else self.data
        return render(self.template_path, data, self.params)

    def render_to(self, path: str) -> None:
        Path(path).write_text(self.render(), encoding="utf-8")

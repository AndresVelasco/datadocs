from __future__ import annotations

from pathlib import Path

import typer


def parse_key_value(values: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for value in values:
        key, separator, item = value.partition("=")
        if not separator or not key:
            raise typer.BadParameter(f"Expected key=value, got {value!r}")
        parsed[key] = item
    return parsed


def write_output(text: str, output: str | None) -> None:
    if output is None:
        typer.echo(text, nl=False)
        return
    Path(output).write_text(text, encoding="utf-8")


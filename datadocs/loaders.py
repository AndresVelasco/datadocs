from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from datadocs.exceptions import DataLoadError


def load_json(path: str) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DataLoadError(f"Could not load JSON data from {path}: {exc}") from exc


def load_yaml(path: str) -> Any:
    try:
        return yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise DataLoadError(f"Could not load YAML data from {path}: {exc}") from exc


def load_ndjson(path: str) -> list[Any]:
    rows: list[Any] = []
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise DataLoadError(f"Could not load NDJSON data from {path}: {exc}") from exc

    for line_number, line in enumerate(lines, start=1):
        try:
            if line.strip():
                rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise DataLoadError(
                f"Could not load NDJSON data from {path} at line {line_number}: {exc}"
            ) from exc
    return rows


def load_data(path: str) -> Any:
    suffix = Path(path).suffix.lower()
    if suffix == ".json":
        return load_json(path)
    if suffix in {".yaml", ".yml"}:
        return load_yaml(path)
    if suffix in {".ndjson", ".jsonl"}:
        return load_ndjson(path)
    raise DataLoadError(f"Unsupported data file extension: {suffix or '<none>'}")

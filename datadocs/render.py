from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateNotFound
from jinja2 import TemplateError as JinjaTemplateError

from datadocs.exceptions import TemplateError


def render(
    template_path: str,
    data: Any,
    params: dict[str, Any] | None = None,
) -> str:
    path = Path(template_path)
    try:
        environment = Environment(
            loader=FileSystemLoader(str(path.parent or ".")),
            undefined=StrictUndefined,
            autoescape=False,
        )
        template = environment.get_template(path.name)
        return template.render(data=data, params=params or {})
    except TemplateNotFound as exc:
        raise TemplateError(f"Template not found: {template_path}") from exc
    except OSError as exc:
        raise TemplateError(f"Could not read template: {template_path}") from exc
    except JinjaTemplateError as exc:
        raise TemplateError(f"Could not render template: {exc}") from exc

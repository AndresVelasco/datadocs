from __future__ import annotations

from typing import Annotated, Literal

import typer

from datadoc._cli_utils import parse_key_value, write_output
from datadoc.document import Document
from datadoc.exceptions import DatadocError
from datadoc.http.source import HttpSource
from datadoc.loaders import load_json

app = typer.Typer(no_args_is_help=True)


@app.command()
def render(
    url: Annotated[str, typer.Option("--url")],
    template: Annotated[str, typer.Option("--template", "-t")],
    method: Annotated[Literal["GET", "POST"], typer.Option("--method")] = "GET",
    output: Annotated[str | None, typer.Option("--output", "-o")] = None,
    header: Annotated[list[str] | None, typer.Option("--header")] = None,
    query_param: Annotated[list[str] | None, typer.Option("--query-param")] = None,
    json_body: Annotated[str | None, typer.Option("--json-body")] = None,
    param: Annotated[list[str] | None, typer.Option("--param")] = None,
) -> None:
    try:
        source = HttpSource(
            url=url,
            method=method,
            headers=parse_key_value(header or []),
            query_params=parse_key_value(query_param or []),
            json_body=load_json(json_body) if json_body else None,
        )
        document = Document(
            template_path=template,
            source=source,
            params=parse_key_value(param or []),
        )
        write_output(document.render(), output)
    except DatadocError as exc:
        raise typer.BadParameter(str(exc)) from exc

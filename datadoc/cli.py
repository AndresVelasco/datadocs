from __future__ import annotations

from typing import Annotated, Any

import typer

from datadoc._cli_utils import parse_key_value, write_output
from datadoc.document import Document
from datadoc.exceptions import DatadocError
from datadoc.loaders import load_data

app = typer.Typer(no_args_is_help=True)


@app.command()
def render(
    template: Annotated[str, typer.Option("--template", "-t")],
    data: Annotated[str, typer.Option("--data", "-d")],
    output: Annotated[str | None, typer.Option("--output", "-o")] = None,
    param: Annotated[list[str] | None, typer.Option("--param")] = None,
) -> None:
    try:
        document = Document(
            template_path=template,
            data=load_data(data),
            params=parse_key_value(param or []),
        )
        write_output(document.render(), output)
    except DatadocError as exc:
        raise typer.BadParameter(str(exc)) from exc


try:
    from datadoc.http.cli import app as http_app

    app.add_typer(http_app, name="http")
except ImportError:  # pragma: no cover
    pass

try:
    from datadoc.bigquery.cli import app as bigquery_app

    app.add_typer(bigquery_app, name="bigquery")
except ImportError:  # pragma: no cover
    pass


def main() -> Any:
    return app()

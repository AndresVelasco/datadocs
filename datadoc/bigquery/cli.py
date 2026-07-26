from __future__ import annotations

from typing import Annotated

import typer

from datadoc._cli_utils import parse_key_value, write_output
from datadoc.bigquery.source import BigQuerySource, QueryParameter
from datadoc.document import Document
from datadoc.exceptions import DatadocError

app = typer.Typer(no_args_is_help=True)


def parse_query_parameters(values: list[str]) -> list[QueryParameter]:
    parameters: list[QueryParameter] = []
    for value in values:
        name_and_type, separator, parameter_value = value.partition("=")
        name, type_separator, type_ = name_and_type.partition(":")
        if not separator or not type_separator or not name or not type_:
            raise typer.BadParameter(
                f"Expected name:TYPE=value for --query-param, got {value!r}"
            )
        parameters.append(QueryParameter(name=name, type_=type_, value=parameter_value))
    return parameters


@app.command()
def render(
    query: Annotated[str, typer.Option("--query")],
    template: Annotated[str, typer.Option("--template", "-t")],
    project: Annotated[str | None, typer.Option("--project")] = None,
    billing_project: Annotated[str | None, typer.Option("--billing-project")] = None,
    location: Annotated[str | None, typer.Option("--location")] = None,
    query_param: Annotated[list[str] | None, typer.Option("--query-param")] = None,
    output: Annotated[str | None, typer.Option("--output", "-o")] = None,
    param: Annotated[list[str] | None, typer.Option("--param")] = None,
) -> None:
    try:
        source = BigQuerySource(
            query_path=query,
            project=project,
            billing_project=billing_project,
            location=location,
            query_parameters=parse_query_parameters(query_param or []),
        )
        document = Document(
            template_path=template,
            source=source,
            params=parse_key_value(param or []),
        )
        write_output(document.render(), output)
    except DatadocError as exc:
        raise typer.BadParameter(str(exc)) from exc

from typer.testing import CliRunner

import datadocs.bigquery.source
import datadocs.http.source
from datadocs.cli import app


def test_cli_render_stdout(tmp_path):
    template = tmp_path / "template.md.j2"
    data = tmp_path / "data.json"
    template.write_text("{{ params.period }}: {{ data.name }}", encoding="utf-8")
    data.write_text('{"name": "Platform"}', encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "render",
            "--template",
            str(template),
            "--data",
            str(data),
            "--param",
            "period=Q2",
        ],
    )

    assert result.exit_code == 0
    assert result.stdout == "Q2: Platform"


def test_cli_render_output(tmp_path):
    template = tmp_path / "template.md.j2"
    data = tmp_path / "data.json"
    output = tmp_path / "output.md"
    template.write_text("{{ data.name }}", encoding="utf-8")
    data.write_text('{"name": "Platform"}', encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "render",
            "--template",
            str(template),
            "--data",
            str(data),
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0
    assert output.read_text(encoding="utf-8") == "Platform"


def test_http_cli_render_uses_source_options(mocker, tmp_path):
    template = tmp_path / "template.md.j2"
    body = tmp_path / "body.json"
    template.write_text("{{ params.period }}: {{ data.name }}", encoding="utf-8")
    body.write_text('{"team": "platform"}', encoding="utf-8")
    load_data = mocker.patch.object(
        datadocs.http.source.HttpSource,
        "load_data",
        return_value={"name": "Platform"},
    )

    result = CliRunner().invoke(
        app,
        [
            "http",
            "render",
            "--url",
            "https://example.com/api",
            "--method",
            "POST",
            "--header",
            "Authorization=Bearer token",
            "--query-param",
            "period=Q2",
            "--json-body",
            str(body),
            "--template",
            str(template),
            "--param",
            "period=Q2",
        ],
    )

    assert result.exit_code == 0
    assert result.stdout == "Q2: Platform"
    load_data.assert_called_once_with()


def test_bigquery_cli_render_uses_source_options(mocker, tmp_path):
    template = tmp_path / "template.md.j2"
    query = tmp_path / "report.sql"
    template.write_text("{{ data[0].name }}", encoding="utf-8")
    query.write_text("select @period as period", encoding="utf-8")
    load_data = mocker.patch.object(
        datadocs.bigquery.source.BigQuerySource,
        "load_data",
        return_value=[{"name": "Platform"}],
    )

    result = CliRunner().invoke(
        app,
        [
            "bigquery",
            "render",
            "--query",
            str(query),
            "--template",
            str(template),
            "--project",
            "runtime-project",
            "--billing-project",
            "billing-project",
            "--location",
            "EU",
            "--query-param",
            "period:STRING=Q2",
        ],
    )

    assert result.exit_code == 0
    assert result.stdout == "Platform"
    load_data.assert_called_once_with()

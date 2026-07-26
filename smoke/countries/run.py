from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

from google.api_core.exceptions import Conflict, NotFound
from google.cloud import bigquery

from datadocs import Document, render
from datadocs.bigquery.source import BigQuerySource
from datadocs.http.source import HttpSource

API_URL = (
    "https://api.restcountries.com/countries/v5"
    "?region=Europe&limit=100&response_fields=names,codes,capitals,population,"
    "region,subregion,currencies,languages,capital_coordinates,borders,timezones,"
    "flag,maps"
)
DATASET_ID_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,1023}$")


def env_bool(name: str, *, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def log(message: str) -> None:
    print(message, file=sys.stderr)


def validate_dataset_id(dataset_id: str) -> None:
    if not DATASET_ID_PATTERN.fullmatch(dataset_id):
        raise RuntimeError(
            "DATADOCS_BQ_DATASET must contain only letters, numbers, and "
            "underscores, and must start with a letter or underscore."
        )


def create_dataset(
    client: bigquery.Client,
    *,
    project: str,
    dataset_id: str,
    location: str,
    table_expiration_hours: int,
    replace: bool,
) -> bool:
    full_dataset_id = f"{project}.{dataset_id}"
    dataset = bigquery.Dataset(full_dataset_id)
    dataset.location = location
    dataset.default_table_expiration_ms = table_expiration_hours * 60 * 60 * 1000
    dataset.labels = {"tool": "datadocs", "kind": "smoke"}

    try:
        client.create_dataset(dataset)
        log(
            f"Created dataset {full_dataset_id}. It will be deleted at the end "
            "unless DATADOCS_SMOKE_KEEP_DATASET=1 is set."
        )
        return True
    except Conflict:
        if not replace:
            log(
                f"Dataset {full_dataset_id} already exists. Reusing it and leaving "
                "it in place after the smoke test."
            )
            return False

        log(
            f"Replacing existing dataset {full_dataset_id}. The recreated dataset "
            "will be deleted at the end unless DATADOCS_SMOKE_KEEP_DATASET=1 is set."
        )
        client.delete_dataset(full_dataset_id, delete_contents=True, not_found_ok=True)
        client.create_dataset(dataset)
        return True


def delete_dataset(client: bigquery.Client, *, project: str, dataset_id: str) -> None:
    try:
        client.delete_dataset(
            f"{project}.{dataset_id}",
            delete_contents=True,
            not_found_ok=True,
        )
    except NotFound:
        return


def authorization_header(token: str) -> str:
    token = token.strip()
    if token.lower().startswith("bearer "):
        return token
    return f"Bearer {token}"


def countries_source(token: str) -> HttpSource:
    return HttpSource(
        url=API_URL,
        headers={"Authorization": authorization_header(token)},
        transform=lambda data: data["data"]["objects"],
    )


def render_template_to_tempfile(template_path: Path, params: dict[str, Any]) -> Path:
    """Render a SQL template to a file for APIs that require query_path.

    The smoke test intentionally exercises BigQuerySource, whose public API accepts
    a SQL file path rather than raw SQL text. Rendering to a temporary file keeps
    the smoke test on that public API while still allowing project/dataset values
    to come from environment-driven params.
    """
    sql = render(str(template_path), data={}, params=params)
    file = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".sql",
        delete=False,
    )
    with file:
        file.write(sql)
    return Path(file.name)


def load_countries_to_bigquery(
    client: bigquery.Client,
    *,
    query: str,
    location: str,
    countries: list[dict[str, Any]],
) -> None:
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(
                "countries_json",
                "STRING",
                json.dumps(countries, sort_keys=True),
            )
        ]
    )
    client.query(query, job_config=job_config, location=location).result()


def main() -> int:
    root = Path(__file__).resolve().parent
    project = require_env("DATADOCS_BQ_PROJECT")
    dataset_id = require_env("DATADOCS_BQ_DATASET")
    countries_token = require_env("DATADOCS_COUNTRIES_API_TOKEN")
    location = os.environ.get("DATADOCS_BQ_LOCATION", "EU")
    table_expiration_hours = int(
        os.environ.get("DATADOCS_SMOKE_TABLE_EXPIRATION_HOURS", "24")
    )
    replace = env_bool("DATADOCS_SMOKE_REPLACE_DATASET")
    keep_dataset = env_bool("DATADOCS_SMOKE_KEEP_DATASET")

    validate_dataset_id(dataset_id)
    if table_expiration_hours < 1:
        raise RuntimeError("DATADOCS_SMOKE_TABLE_EXPIRATION_HOURS must be >= 1.")

    client = bigquery.Client(project=project, location=location)
    created_dataset = False
    load_sql_file: Path | None = None
    report_query_file: Path | None = None

    try:
        log(f"Preparing dataset {project}.{dataset_id} in {location}...")
        created_dataset = create_dataset(
            client,
            project=project,
            dataset_id=dataset_id,
            location=location,
            table_expiration_hours=table_expiration_hours,
            replace=replace,
        )

        log("Fetching REST Countries data...")
        countries = countries_source(countries_token).load_data()
        log(f"Fetched {len(countries)} countries.")

        params = {
            "project": project,
            "dataset": dataset_id,
            "table_expiration_hours": table_expiration_hours,
        }

        load_sql_file = render_template_to_tempfile(
            root / "load_to_bigquery.sql.j2",
            params,
        )
        log("Loading countries into BigQuery...")
        load_countries_to_bigquery(
            client,
            query=load_sql_file.read_text(encoding="utf-8"),
            location=location,
            countries=countries,
        )

        report_query_file = render_template_to_tempfile(
            root / "report_query.sql.j2",
            params,
        )
        report_source = BigQuerySource(
            query_path=str(report_query_file),
            project=project,
            billing_project=project,
            location=location,
        )
        report = Document(
            template_path=str(root / "report.md.j2"),
            source=report_source,
            params=params,
        )

        print(report.render())
        return 0
    finally:
        for path in (load_sql_file, report_query_file):
            if path is not None:
                path.unlink(missing_ok=True)

        if created_dataset and not keep_dataset:
            log(f"Deleting dataset {project}.{dataset_id}...")
            delete_dataset(client, project=project, dataset_id=dataset_id)
        elif created_dataset:
            log(f"Keeping dataset {project}.{dataset_id} for inspection.")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Smoke test failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

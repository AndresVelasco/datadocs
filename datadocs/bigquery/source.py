from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from datadocs.exceptions import SourceError


@dataclass(frozen=True)
class QueryParameter:
    name: str
    type_: str
    value: str


class BigQuerySource:
    def __init__(
        self,
        *,
        query_path: str,
        project: str | None = None,
        billing_project: str | None = None,
        location: str | None = None,
        query_parameters: list[QueryParameter] | None = None,
    ) -> None:
        self.query_path = query_path
        self.project = project
        self.billing_project = billing_project
        self.location = location
        self.query_parameters = query_parameters or []

    def load_data(self) -> list[dict[str, Any]]:
        try:
            from google.cloud import bigquery
        except ImportError as exc:
            raise SourceError(
                "BigQuery integration requires the 'bigquery' extra: "
                "pip install datadocs[bigquery]"
            ) from exc

        try:
            query = Path(self.query_path).read_text(encoding="utf-8")
            client = bigquery.Client(
                project=self.project,
                location=self.location,
            )
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter(
                        parameter.name,
                        parameter.type_,
                        parameter.value,
                    )
                    for parameter in self.query_parameters
                ]
            )
            job = client.query(
                query,
                job_config=job_config,
                project=self.billing_project,
                location=self.location,
            )
            return [dict(row.items()) for row in job.result()]
        except OSError as exc:
            raise SourceError(
                f"Could not read BigQuery query file: {self.query_path}"
            ) from exc
        except Exception as exc:
            raise SourceError(f"BigQuery query failed: {exc}") from exc

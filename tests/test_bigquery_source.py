import sys
import types

from datadoc.bigquery.source import BigQuerySource, QueryParameter


class Row:
    def __init__(self, values):
        self.values = values

    def items(self):
        return self.values.items()


class Job:
    def result(self):
        return [Row({"name": "Platform"})]


def test_bigquery_source_loads_rows(monkeypatch, tmp_path):
    query_path = tmp_path / "report.sql"
    query_path.write_text("select @period as period", encoding="utf-8")
    calls = {}

    class ScalarQueryParameter:
        def __init__(self, name, type_, value):
            calls["parameter"] = (name, type_, value)

    class QueryJobConfig:
        def __init__(self, query_parameters):
            calls["query_parameters"] = query_parameters

    class Client:
        def __init__(self, project=None, location=None):
            calls["client"] = (project, location)

        def query(self, query, job_config=None, project=None, location=None):
            calls["query"] = (query, job_config, project, location)
            return Job()

    bigquery = types.SimpleNamespace(
        Client=Client,
        QueryJobConfig=QueryJobConfig,
        ScalarQueryParameter=ScalarQueryParameter,
    )
    google_cloud = types.ModuleType("google.cloud")
    google_cloud.bigquery = bigquery
    monkeypatch.setitem(sys.modules, "google", types.ModuleType("google"))
    monkeypatch.setitem(sys.modules, "google.cloud", google_cloud)
    monkeypatch.setitem(sys.modules, "google.cloud.bigquery", bigquery)

    source = BigQuerySource(
        query_path=str(query_path),
        project="runtime-project",
        billing_project="billing-project",
        location="EU",
        query_parameters=[QueryParameter("period", "STRING", "Q2")],
    )

    assert source.load_data() == [{"name": "Platform"}]
    assert calls["client"] == ("runtime-project", "EU")
    assert calls["parameter"] == ("period", "STRING", "Q2")
    assert calls["query"][0] == "select @period as period"
    assert calls["query"][2:] == ("billing-project", "EU")


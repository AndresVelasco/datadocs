# Countries Smoke Test

This smoke test exercises `datadocs` against the real REST Countries API and real
BigQuery using Google Application Default Credentials.

It does not run as part of the normal test suite.

## Flow

```text
REST Countries API
  -> datadocs HttpSource
  -> load_to_bigquery.sql.j2
  -> BigQuery dataset/table
  -> report_query.sql.j2
  -> datadocs BigQuerySource
  -> report.md.j2
  -> Markdown report
```

## Requirements

Install the optional integrations:

```bash
uv sync --extra dev --extra http --extra bigquery
```

Authenticate with Google ADC:

```bash
gcloud auth application-default login
```

Configure the destination:

```bash
export DATADOCS_BQ_PROJECT=bigquery-sandbox-cpvuft6h
export DATADOCS_BQ_DATASET=test_datadocs
export DATADOCS_BQ_LOCATION=EU
export DATADOCS_COUNTRIES_API_TOKEN=your-rest-countries-token
```

Run:

```bash
uv run python smoke/countries/run.py
```

The script ensures `DATADOCS_BQ_DATASET` exists with a default table expiration
policy, loads a `countries` table, and renders a Markdown report to stdout.
Progress and cleanup logs are written to stderr.

## Safety Controls

If the configured dataset already exists, the smoke test reuses it and leaves it
in place after the run.

If the smoke test creates the dataset, it deletes that dataset by default at the
end. To keep a newly created dataset for inspection:

```bash
export DATADOCS_SMOKE_KEEP_DATASET=1
```

To delete and recreate an existing configured dataset before running:

```bash
export DATADOCS_SMOKE_REPLACE_DATASET=1
```

A recreated dataset is treated as created by the smoke test and is deleted at the
end unless `DATADOCS_SMOKE_KEEP_DATASET=1` is set.

To change table expiration:

```bash
export DATADOCS_SMOKE_TABLE_EXPIRATION_HOURS=24
```

## Example Output

```markdown
# REST Countries BigQuery Smoke Report

Project: `bigquery-sandbox-cpvuft6h`

Dataset: `test_datadocs`

Rows shown: 20

## 1. Bangladesh

- Official name: People's Republic of Bangladesh
- Capital: n/a
- Region: Asia / Southern Asia
- Population: 169,828,911
- Languages JSON: `[{"bcp47":"bn","iso639_1":"bn","iso639_2b":"ben","iso639_2t":"ben","iso639_3":"ben","name":"Bengali","native_name":"বাংলা"}]`
- Currencies JSON: `[{"code":"BDT","name":"Bangladeshi taka","symbol":"৳"}]`
- Map: n/a

## 2. Algeria
```

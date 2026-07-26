# datadocs

Generate documents from structured data.

`datadocs` generates Markdown, HTML, or text documents from structured data using
Jinja templates.

The philosophy is simple:

> Bring your own data. Bring your own template. Generate documents deterministically.

## What it is

`datadocs` is a small Python package for rendering documents from data you already
prepared.

Templates receive exactly two variables:

```python
data
params
```

## What it is not

`datadocs` is not a workflow engine, reporting platform, data transformation
framework, query builder, or AI framework.

## Installation

```bash
pip install datadocs
```

Optional integrations:

```bash
pip install "datadocs[http]"
pip install "datadocs[bigquery]"
```

## CLI

Render from JSON, YAML, or NDJSON:

```bash
datadocs render \
  --template report.md.j2 \
  --data report.json
```

Write to a file:

```bash
datadocs render \
  --template report.md.j2 \
  --data report.yaml \
  --output report.md
```

Pass template parameters:

```bash
datadocs render \
  --template report.md.j2 \
  --data report.ndjson \
  --param period="Q2 2026"
```

## SDK

```python
from datadocs import render

markdown = render(
    template_path="templates/report.md.j2",
    data={"epics": [{"name": "Search"}]},
    params={"period": "Q2 2026"},
)
```

Use `Document` with data:

```python
from datadocs import Document

doc = Document(
    template_path="templates/report.md.j2",
    data={"epics": [{"name": "Search"}]},
    params={"period": "Q2 2026"},
)

doc.render_to("report.md")
```

Use `Document` with a source:

```python
doc = Document(
    template_path="templates/report.md.j2",
    source=my_source,
)
```

A source only needs to provide:

```python
def load_data(self):
    ...
```

## Architecture

`datadocs` has one deterministic rendering path:

```text
Source or prepared data -> Document -> render() -> text
```

The renderer only knows about templates and data. It does not know whether data
came from a file, HTTP API, BigQuery query, or a custom source.

### Rendering

`render()` is the core function:

```python
render(template_path, data, params=None)
```

It loads a Jinja template from disk and renders it with exactly two template
variables:

```python
data
params
```

This keeps templates predictable and avoids hidden context.

### Documents

`Document` is a small wrapper around the rendering contract. It accepts either
prepared `data` or a `source`, never both:

```python
Document(template_path="report.md.j2", data=data)
Document(template_path="report.md.j2", source=source)
```

`doc.render()` returns text. `doc.render_to(path)` writes that text to disk.

### Sources

A source is any object with:

```python
def load_data(self):
    ...
```

Sources are responsible only for loading ordinary Python data. They should not
render templates, transform data, build queries, or manage workflows.

Built-in sources follow that rule:

| Source | Responsibility |
| --- | --- |
| `HttpSource` | Make one HTTP request and return the parsed JSON response. |
| `BigQuerySource` | Execute one supplied SQL file and return query rows as dictionaries. |

Custom sources can be added without changing the renderer:

```python
class MySource:
    def load_data(self):
        return {"epics": [{"name": "Search"}]}


doc = Document(template_path="report.md.j2", source=MySource())
```

### Loaders

File loaders are intentionally separate from sources. The CLI uses loaders for
JSON, YAML, and NDJSON files, while integrations use sources.

## HTTP

HTTP auth is passed through headers. `datadocs` does not manage credentials.

```bash
datadocs http render \
  --url https://example.com/api \
  --header "Authorization=Bearer $TOKEN" \
  --query-param period="Q2 2026" \
  --template report.md.j2
```

POST JSON from a file:

```bash
datadocs http render \
  --url https://example.com/api \
  --method POST \
  --json-body request.json \
  --template report.md.j2
```

The parsed JSON response is used directly as `data`.

## BigQuery

BigQuery authentication uses Google Application Default Credentials. `datadocs`
does not expose credential flags.

```bash
datadocs bigquery render \
  --query queries/report.sql \
  --template report.md.j2 \
  --project runtime-project \
  --billing-project billing-project \
  --location EU
```

Typed query parameters use `name:TYPE=value`:

```bash
datadocs bigquery render \
  --query queries/report.sql \
  --template report.md.j2 \
  --query-param period:STRING="Q2 2026"
```

The SQL file is executed as supplied. `datadocs` does not build or transform
queries.

## Template example

```jinja2
# Delivery Report

Period: {{ params.period }}

{% for epic in data.epics %}
## {{ epic.name }}
{% endfor %}
```

## Future integrations

Future integrations such as `datadocs.langchain` should be optional layers on top
of the deterministic rendering pipeline.

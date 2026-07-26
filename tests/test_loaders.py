import pytest

from datadocs.exceptions import DataLoadError
from datadocs.loaders import load_data, load_json, load_ndjson, load_yaml


def test_load_json(tmp_path):
    path = tmp_path / "data.json"
    path.write_text('{"name": "Platform"}', encoding="utf-8")

    assert load_json(str(path)) == {"name": "Platform"}


def test_load_yaml(tmp_path):
    path = tmp_path / "data.yaml"
    path.write_text("name: Platform\n", encoding="utf-8")

    assert load_yaml(str(path)) == {"name": "Platform"}


def test_load_ndjson(tmp_path):
    path = tmp_path / "data.ndjson"
    path.write_text('{"id": 1}\n{"id": 2}\n', encoding="utf-8")

    assert load_ndjson(str(path)) == [{"id": 1}, {"id": 2}]


def test_load_data_rejects_unknown_extension(tmp_path):
    path = tmp_path / "data.txt"
    path.write_text("x", encoding="utf-8")

    with pytest.raises(DataLoadError):
        load_data(str(path))


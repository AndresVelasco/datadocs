import pytest

from datadocs import Document
from datadocs.exceptions import ConfigurationError


class StaticSource:
    def load_data(self):
        return {"name": "Source"}


def test_document_renders_data(tmp_path):
    template = tmp_path / "template.md.j2"
    template.write_text("{{ data.name }}", encoding="utf-8")

    document = Document(template_path=str(template), data={"name": "Data"})

    assert document.render() == "Data"


def test_document_renders_source(tmp_path):
    template = tmp_path / "template.md.j2"
    template.write_text("{{ data.name }}", encoding="utf-8")

    document = Document(template_path=str(template), source=StaticSource())

    assert document.render() == "Source"


def test_document_rejects_data_and_source(tmp_path):
    with pytest.raises(ConfigurationError):
        Document(
            template_path=str(tmp_path / "template.md.j2"),
            data={},
            source=StaticSource(),
        )


def test_document_render_to(tmp_path):
    template = tmp_path / "template.md.j2"
    output = tmp_path / "output.md"
    template.write_text("{{ data.name }}", encoding="utf-8")

    Document(template_path=str(template), data={"name": "Data"}).render_to(str(output))

    assert output.read_text(encoding="utf-8") == "Data"

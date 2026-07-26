from datadoc import render


def test_render_passes_data_and_params(tmp_path):
    template = tmp_path / "report.md.j2"
    template.write_text("{{ params.period }}: {{ data.name }}", encoding="utf-8")

    result = render(str(template), {"name": "Platform"}, {"period": "Q2"})

    assert result == "Q2: Platform"


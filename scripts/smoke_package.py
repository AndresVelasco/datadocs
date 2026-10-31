"""Check an installed distribution's version and render via the SDK and CLI."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sysconfig
import tempfile
from importlib.metadata import version
from pathlib import Path

from datadocs import Document, render


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("expected_version")
    args = parser.parse_args()
    installed = version("datadocs")
    assert installed == args.expected_version, (installed, args.expected_version)

    with tempfile.TemporaryDirectory(prefix="datadocs-package-smoke-") as directory:
        root = Path(directory)
        template = root / "report.md.j2"
        data_file = root / "data.json"
        template.write_text("{{ params.period }}: {{ data.name }}", encoding="utf-8")
        data = {"name": "datadocs"}
        data_file.write_text(json.dumps(data), encoding="utf-8")
        params = {"period": "release"}
        expected = "release: datadocs"
        assert render(str(template), data, params) == expected
        document = Document(
            template_path=str(template), data=data, params=params
        )
        assert document.render() == expected

        executable = Path(sysconfig.get_path("scripts")) / (
            "datadocs.exe" if os.name == "nt" else "datadocs"
        )
        result = subprocess.run(
            [
                str(executable),
                "render",
                "--template",
                str(template),
                "--data",
                str(data_file),
                "--param",
                "period=release",
            ],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
        assert result.stdout == expected, result.stdout
    print(f"datadocs {installed}: SDK and installed CLI rendering passed")


if __name__ == "__main__":
    main()

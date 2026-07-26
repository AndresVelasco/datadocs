import pytest

from datadocs.exceptions import SourceError
from datadocs.http.source import HttpSource


class Response:
    def raise_for_status(self):
        return None

    def json(self):
        return {"name": "Platform"}


def test_http_source_loads_json(mocker):
    request = mocker.patch("httpx.request", return_value=Response())

    source = HttpSource(
        url="https://example.com/api",
        method="POST",
        headers={"Authorization": "Bearer token"},
        query_params={"period": "Q2"},
        json_body={"team": "platform"},
    )

    assert source.load_data() == {"name": "Platform"}
    request.assert_called_once_with(
        "POST",
        "https://example.com/api",
        headers={"Authorization": "Bearer token"},
        params={"period": "Q2"},
        json={"team": "platform"},
    )


def test_http_source_transforms_json(mocker):
    mocker.patch(
        "httpx.request",
        return_value=Response(),
    )

    source = HttpSource(
        url="https://example.com/api",
        transform=lambda data: data["name"],
    )

    assert source.load_data() == "Platform"


def test_http_source_rejects_unsupported_response_format():
    source = HttpSource(
        url="https://example.com/api",
        response_format="text",  # type: ignore[arg-type]
    )

    with pytest.raises(SourceError, match="Unsupported HTTP response format"):
        source.load_data()

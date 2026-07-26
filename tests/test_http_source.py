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


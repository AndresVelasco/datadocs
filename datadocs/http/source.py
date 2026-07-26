from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal

from datadocs.exceptions import SourceError


class HttpSource:
    def __init__(
        self,
        *,
        url: str,
        method: Literal["GET", "POST"] = "GET",
        headers: dict[str, str] | None = None,
        query_params: dict[str, str] | None = None,
        json_body: Any | None = None,
        response_format: Literal["json"] = "json",
        transform: Callable[[Any], Any] | None = None,
    ) -> None:
        self.url = url
        self.method = method
        self.headers = headers or {}
        self.query_params = query_params or {}
        self.json_body = json_body
        self.response_format = response_format
        self.transform = transform

    def load_data(self) -> Any:
        try:
            import httpx
        except ImportError as exc:
            raise SourceError(
                "HTTP integration requires the 'http' extra: pip install datadocs[http]"
            ) from exc

        if self.response_format != "json":
            raise SourceError(
                f"Unsupported HTTP response format: {self.response_format}"
            )

        try:
            response = httpx.request(
                self.method,
                self.url,
                headers=self.headers,
                params=self.query_params,
                json=self.json_body,
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as exc:
            raise SourceError(f"HTTP request failed: {exc}") from exc
        except ValueError as exc:
            raise SourceError("HTTP response did not contain valid JSON") from exc

        if self.transform is None:
            return data
        return self.transform(data)

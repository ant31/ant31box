#!/usr/bin/env python3
import json
import logging
from typing import Any, Literal, TypeVar
from urllib.parse import ParseResult, urlparse

import aiohttp
from pydantic import BaseModel, ConfigDict, Field

from ant31box.version import VERSION

logger = logging.getLogger(__name__)

T = TypeVar("T")  # , bound="ClientConfig")
# pylint: disable=protected-access


class ClientConfig(BaseModel):
    model_config: ConfigDict = ConfigDict(extra="allow")
    endpoint: str = Field(default="http://localhost:8080")
    client_name: str = Field(default="client")
    verify_tls: bool = Field(default=True)
    session_args: tuple[list, dict[str, Any]] = Field(default=([], {}))


class BaseClient:
    def __init__(
        self,
        endpoint: str,
        verify_tls: bool = True,
        session_args: tuple[list, dict[str, Any]] = ([], {}),
        client_name: str = "client",
    ) -> None:
        self._session: aiohttp.ClientSession | None = None
        self.client_config = ClientConfig(
            endpoint=endpoint, verify_tls=verify_tls, session_args=session_args, client_name=client_name
        )
        self._endpoint: ParseResult = self._configure_endpoint(self.client_config.endpoint)
        self._headers: dict[str, str] = {
            "Content-Type": "application/json",
            "User-Agent": f"ant31box-cli/{self.client_config.client_name}-{VERSION.app_version}",
        }

    @property
    def endpoint(self) -> ParseResult:
        return self._endpoint

    @endpoint.setter
    def endpoint(self, value: str) -> None:
        self._endpoint = self._configure_endpoint(value)

    @property
    def ssl_mode(self) -> bool:
        return self.client_config.verify_tls

    def close(self):
        """
        Close aiohttp.ClientSession.

        This is useful to be called manually in tests if each test when each test uses a new loop. After close, new
        requests will automatically create a new session.

        Note: We need a sync version for `__del__` and `aiohttp.ClientSession.close()` is async even though it doesn't
        have to be.
        """
        if self._session:
            if not self._session.closed:
                # Older aiohttp does not have _connector_owner
                if not hasattr(self._session, "_connector_owner") or self._session._connector_owner:
                    try:
                        if self._session._connector:
                            self._session._connector._close()  # New version returns a coroutine in close() as warning
                    except Exception:  # pylint: disable=broad-exception-caught
                        if self._session._connector:
                            self._session._connector.close()
                self._session._connector = None
            self._session = None

    @property
    def session(self) -> aiohttp.ClientSession:
        """An instance of aiohttp.ClientSession"""
        if not self._session or self._session.closed or not self._session._loop or self._session._loop.is_closed():
            self._session = aiohttp.ClientSession(
                *self.client_config.session_args[0], **self.client_config.session_args[1]
            )
        return self._session

    # pylint: disable=too-many-arguments
    async def log_request(self, resp: aiohttp.ClientResponse) -> None:
        try:
            raw = await resp.read()
        except aiohttp.ClientPayloadError:
            raw = b""
        try:
            logger.debug(
                json.dumps(
                    {
                        "query": {
                            "url": str(resp.request_info.url),
                            "method": resp.request_info.method,
                            "headers": dict(resp.request_info.headers.items()),
                        },
                        "response": {
                            "headers": dict(resp.headers.items()),
                            "status": resp.status,
                            "raw": raw.decode("utf-8"),
                        },
                    },
                    default=str,
                )
            )
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    def _url(self, path: str, endpoint: str = "") -> str:
        """Construct the url from a relative path"""
        if endpoint:
            ep = urlparse(endpoint)
        else:
            ep = self.endpoint
        return ep.geturl() + path

    def _configure_endpoint(self, endpoint: str) -> ParseResult:
        return urlparse(endpoint)

    def headers(
        self,
        content_type: Literal["json", "form"] | str | None = None,
        extra: dict[str, str] | None = None,
    ) -> dict[str, str]:
        headers: dict[str, str] = {}
        headers.update(self._headers)

        if content_type == "json":
            headers["Content-Type"] = "application/json"
        elif content_type == "form":
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        elif content_type:
            headers["Content-Type"] = content_type

        if extra:
            headers.update(extra)

        return headers

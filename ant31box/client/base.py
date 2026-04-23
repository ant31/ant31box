#!/usr/bin/env python3
import asyncio
import contextlib
import json
import logging
from typing import Any, Literal, TypeVar
from urllib.parse import ParseResult, urlparse

import httpx
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
        self._session: httpx.AsyncClient | None = None
        self._background_tasks: set[asyncio.Task] = set()
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
        Close httpx.AsyncClient.

        This is useful to be called manually in tests if each test when each test uses a new loop. After close, new
        requests will automatically create a new session.
        """
        if self._session:
            if not self._session.is_closed:
                try:
                    loop = asyncio.get_running_loop()
                    task = loop.create_task(self._session.aclose())
                    self._background_tasks.add(task)
                    task.add_done_callback(self._background_tasks.discard)
                except RuntimeError:
                    pass
            self._session = None

    @property
    def session(self) -> httpx.AsyncClient:
        """An instance of httpx.AsyncClient that auto-recreates for different event loops."""
        needs_new_session = (
            not self._session
            or self._session.is_closed
        )

        if needs_new_session:
            self._session = httpx.AsyncClient(
                *self.client_config.session_args[0],
                verify=self.client_config.verify_tls,
                follow_redirects=True,
                **self.client_config.session_args[1]
            )

        return self._session

    # pylint: disable=too-many-arguments
    async def log_request(self, resp: httpx.Response) -> None:
        try:
            await resp.aread()
            raw = resp.content
        except Exception:
            raw = b""
        with contextlib.suppress(Exception):
            logger.debug(
                json.dumps(
                    {
                        "query": {
                            "url": str(resp.request.url),
                            "method": resp.request.method,
                            "headers": dict(resp.request.headers.items()),
                        },
                        "response": {
                            "headers": dict(resp.headers.items()),
                            "status": resp.status_code,
                            "raw": raw.decode("utf-8", errors="replace"),
                        },
                    },
                    default=str,
                )
            )

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

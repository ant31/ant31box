from collections.abc import Sequence

from starlette.datastructures import URL, Headers, QueryParams
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from ..exception import UnauthorizedAccess


class TokenAuthMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        token: str = "",
        parameter: str | None = "auth_token",
        header_name: str | None = "token",
        skip_paths: Sequence[str] = [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/metrics",
            "/health",
        ],
    ) -> None:
        self.token: str = token
        self.app = app
        self.parameter: str | None = parameter
        self.header_name: str | None = header_name
        self.skip_paths: set[str] = set(skip_paths)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        headers = Headers(scope=scope)
        url = URL(scope=scope)
        path = url.path
        params = QueryParams(scope=scope)

        # if token is not set or path is in skip_paths then skip
        # if token is set and matches with parameter or header then allow
        if (
            (not self.token or path in self.skip_paths)
            or (self.parameter and self.parameter in params and params[self.parameter] == self.token)
            or (self.header_name and self.header_name in headers and headers[self.header_name] == self.token)
        ):
            await self.app(scope, receive, send)
            return

        # if token is set and doesn't match then return UnauthorizedAccess error
        error = UnauthorizedAccess("NoAuth")
        await JSONResponse({"error": error.to_dict()}, status_code=error.status_code)(scope, receive, send)
        return

from typing import ClassVar

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette_exporter import handle_metrics
from starlette_exporter.middleware import PrometheusMiddleware
from uvicorn.importer import import_from_string
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from ant31box.config import Config, FastAPIConfigSchema, config
from ant31box.init import init

from .middlewares.errors import catch_exceptions_middleware
from .middlewares.process_time import add_process_time_header
from .middlewares.token import TokenAuthMiddleware


def cors(server: "Server"):
    server.app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=server.config.cors.allow_origin_regex,
        allow_origins=server.config.cors.allow_origins,
        allow_credentials=server.config.cors.allow_credentials,
        allow_methods=server.config.cors.allow_methods,
        allow_headers=server.config.cors.allow_headers,
    )


def add_process_time_header_m(server: "Server"):
    server.app.middleware("http")(add_process_time_header)


def token_auth(server: "Server"):
    if server.config.token is not None:
        server.config.token_auth.token = server.config.token

    server.app.add_middleware(
        TokenAuthMiddleware,
        token=server.config.token_auth.token,
        parameter=server.config.token_auth.parameter,
        header_name=server.config.token_auth.header_name,
        skip_paths=server.config.token_auth.skip_paths,
    )


def catch_exceptions(server: "Server"):
    server.app.middleware("http")(catch_exceptions_middleware)


def prometheus(server: "Server"):
    server.app.add_middleware(PrometheusMiddleware, app_name=server.appname)
    server.app.add_route("/metrics", handle_metrics)


def proxy_headers(server: "Server"):
    server.app.add_middleware(ProxyHeadersMiddleware)


AVAILABLE_MIDDLEWARES = {
    "cors": "ant31box.server.server:cors",
    "tokenAuth": "ant31box.server.server:token_auth",
    "catchExceptions": "ant31box.server.server:catch_exceptions",
    "prometheus": "ant31box.server.server:prometheus",
    "proxyHeaders": "ant31box.server.server:proxy_headers",
    "addProcessTimeHeader": "ant31box.server.server:add_process_time_header_m",
}
DEFAULT_MIDDLEWARES = {"catchExceptions", "prometheus", "proxyHeaders", "addProcessTimeHeader"}
AVAILABLE_ROUTERS = {"ant31box.server.api.info:router", "ant31box.server.api.debug:router"}


class Server:
    _available_middlewares: ClassVar[dict[str, str]] = AVAILABLE_MIDDLEWARES
    _default_middlewares: ClassVar[set[str]] = DEFAULT_MIDDLEWARES
    _default_routers: ClassVar[set[str]] = AVAILABLE_ROUTERS

    _routers: ClassVar[set[str]] = set()
    _middlewares: ClassVar[set[str]] = set()

    def __init__(self, conf: FastAPIConfigSchema, appname="ant31box", appenv="dev"):
        self.config: FastAPIConfigSchema = conf
        self.app: FastAPI = FastAPI()
        self.appname = appname
        self.appenv = appenv

        defaultm = self._default_middlewares
        if self.config.middlewares_replace_default is not None:
            defaultm = self.config.middlewares_replace_default
        middlewares = set(self.config.middlewares).union(defaultm).union(self._middlewares)
        self.load_middlewares(middlewares)

        defaultr = self._default_routers
        if self.config.routers_replace_default is not None:
            defaultr = self.config.routers_replace_default
        routers = set(self.config.routers).union(defaultr).union(self._routers)
        self.load_routers(routers)

    @classmethod
    def set_available_middlewares(cls, middlewares: dict[str, str]):
        cls._available_middlewares = middlewares

    @classmethod
    def add_available_middlewares(cls, middlewares: dict[str, str]):
        cls._available_middlewares.update(middlewares)

    def load_middlewares(self, middlewares: set[str]):
        loaded = set()
        for middleware in middlewares:
            importname = middleware
            if middleware in self._available_middlewares:
                importname = self._available_middlewares[middleware]
            if importname in loaded:
                # already loaded
                continue
            callback = import_from_string(importname)
            callback(self)
            loaded.add(importname)

    def load_routers(self, routers: set[str]):
        debugr = "ant31box.server.api.debug:router"
        if self.appenv in ["prod", "production"] and debugr in routers:
            routers.remove(debugr)
        for router in routers:
            self.app.include_router(import_from_string(router))


def serve_from_config(conf: Config, server_class: type[Server] = Server) -> FastAPI:
    init(conf.conf, "fastapi")
    if not issubclass(server_class, Server):
        raise TypeError(f"server must be a subclass or instance of {Server}")

    server = server_class(conf.server, conf.name, conf.app.env)
    return server.app


# override this method to use a different server class/config
def serve() -> FastAPI:
    return serve_from_config(config(), Server)

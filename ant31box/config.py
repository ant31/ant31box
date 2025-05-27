# pylint: disable=no-self-argument

import json
import logging
import logging.config
import os
from typing import Any, Generic, Self, TypeVar

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from ant31box.utilsd import deepmerge

LOG_LEVELS: dict[str, int] = {
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
}

LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "ant31box.logutils.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": None,
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "level": "INFO",
        },
    },
    "loggers": {
        "ant31box": {"handlers": ["default"], "level": "INFO", "propagate": True},
    },
}


logger: logging.Logger = logging.getLogger("ant31box")


class BaseConfig(BaseModel):
    model_config = ConfigDict(extra="allow")


class AppConfigSchema(BaseConfig):
    env: str = Field(default="dev")
    prometheus_dir: str = Field(default="/tmp/prometheus")


class CorsConfigSchema(BaseConfig):
    allow_origin_regex: str = Field(default=".*")
    allow_origins: list[str] = Field(
        default=[
            "http://localhost:8080",
            "http://localhost:8000",
            "http://localhost",
        ]
    )
    allow_credentials: bool = Field(default=False)
    allow_methods: list[str] = Field(default=["*"])
    allow_headers: list[str] = Field(default=["*"])


class TokenAuthMiddleWare(BaseConfig):
    token: str = Field(default="")
    parameter: str = Field(default="token_auth")
    header_name: str = Field(default="token")
    skip_paths: list[str] = Field(
        default=[
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/metrics",
            "/health",
        ]
    )


class FastAPIConfigSchema(BaseConfig):
    server: str = Field(default="ant31box.server.server:serve")
    middlewares: list[str] = Field(default_factory=list)
    routers: list[str] = Field(default_factory=list)
    middlewares_replace_default: list[str] | None = Field(
        default=None, description="Replace default middlewares, if set to None, default middlewares are added"
    )
    routers_replace_default: list[str] | None = Field(
        default=None, description="Replace default routers, if set to None, default routers are added"
    )
    cors: CorsConfigSchema = Field(default_factory=CorsConfigSchema)
    token_auth: TokenAuthMiddleWare = Field(default_factory=TokenAuthMiddleWare)
    token: str = Field(default="")
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8080)
    reload: bool = Field(default=False)

    @field_validator("port")
    def convert_port(cls, v) -> int:
        return int(v)


class LoggingConfigSchema(BaseConfig):
    use_colors: bool = Field(default=True)
    log_config: dict[str, Any] | str | None = Field(default_factory=lambda: LOGGING_CONFIG)
    level: str = Field(default="info")


class SentryConfigSchema(BaseConfig):
    dsn: str | None = Field(default=None)
    environment: str | None = Field(default=None)
    release: str | None = Field(default=None)
    traces_sample_rate: float | None = Field(default=None)


ENVPREFIX = "ANT31BOX"


class S3ConfigSchema(BaseConfig):
    endpoint: str = Field(default="https://s3.eu-central-1.amazonaws.com")
    access_key: str = Field(default="")
    secret_key: str = Field(default="")
    region: str = Field(default="eu-central-1")
    prefix: str = Field(default="")
    bucket: str = Field(default="abucket")


# Main configuration schema
class ConfigSchema(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix=f"{ENVPREFIX}_", env_nested_delimiter="__", case_sensitive=False, extra="allow"
    )
    app: AppConfigSchema = Field(default_factory=AppConfigSchema)
    logging: LoggingConfigSchema = Field(default_factory=LoggingConfigSchema)
    server: FastAPIConfigSchema = Field(default_factory=FastAPIConfigSchema)
    sentry: SentryConfigSchema = Field(default_factory=SentryConfigSchema)
    name: str = Field(default="ant31box")


TBaseConfig = TypeVar("TBaseConfig", bound=BaseSettings)  # pylint: disable= invalid-name


class GenericConfig(Generic[TBaseConfig]):
    _env_prefix = ENVPREFIX
    __config_class__: type[TBaseConfig]

    def __init__(self, conf: TBaseConfig):
        self.loaded = False
        self._conf: TBaseConfig = conf
        self._set_conf(conf)

    @property
    def conf(self) -> TBaseConfig:
        return self._conf

    @property
    def logging(self) -> LoggingConfigSchema:
        return LoggingConfigSchema()

    @property
    def name(self) -> str:
        return "app"

    def _set_conf(self, conf: TBaseConfig) -> None:
        self._conf = conf
        self.load(force=True)

    def load(self, force=True) -> bool:
        if not self.loaded or force:
            self.configure_logging()
            self.loaded = True
            return True
        raise RuntimeError("Config already loaded")

    def configure_logging(self) -> None:
        log_config = self.logging.log_config
        use_colors = self.logging.use_colors
        log_level = self.logging.level

        if log_config:
            loaded_config = None
            if isinstance(log_config, dict):
                if use_colors in (True, False):
                    log_config["formatters"]["default"]["use_colors"] = use_colors
                loaded_config = log_config

            elif log_config.endswith(".json"):
                with open(log_config, encoding="utf-8") as file:
                    loaded_config = json.load(file)

            elif log_config.endswith((".yaml", ".yml")):
                with open(log_config, encoding="utf-8") as file:
                    loaded_config = yaml.safe_load(file)
            else:
                # See the note about fileConfig() here:
                # https://docs.python.org/3/library/logging.config.html#configuration-file-format
                logging.config.fileConfig(log_config, disable_existing_loggers=False)
            if loaded_config is not None:
                if (
                    "loggers" in loaded_config
                    and self.name not in loaded_config["loggers"]
                    and "ant31box" in loaded_config["loggers"]
                ):
                    loaded_config["loggers"][self.name] = loaded_config["loggers"]["ant31box"]
                logging.config.dictConfig(loaded_config)

        if log_level is not None:
            if isinstance(log_level, str):
                log_level = LOG_LEVELS[log_level.lower()]
            logging.getLogger(self.name).setLevel(log_level)
            logging.getLogger("ant31box").setLevel(log_level)
            logging.getLogger("root").setLevel(log_level)

    @classmethod
    def from_yaml(cls, file_path: str) -> Self:
        with open(file_path, encoding="utf-8") as file:
            config_dict = yaml.safe_load(file)
        # merge init + env config
        alreadyinit = cls.__config_class__().model_dump(exclude_unset=True, exclude_defaults=True)
        deepmerge(config_dict, alreadyinit)
        logger.debug("Config loaded from %s: %s", file_path, config_dict)

        return cls(cls.__config_class__.model_validate(config_dict))

    @classmethod
    def default_config(cls) -> Self:
        return cls(cls.__config_class__())

    @classmethod
    def auto_config(cls, path: str | None = None) -> Self:
        if path:
            paths = [path]
        else:
            paths = [
                os.environ.get(f"{cls._env_prefix}_CONFIG", "localconfig.yaml"),
                "config.yaml",
            ]
        conf = cls.default_config()
        matched = False
        for p in paths:
            if os.path.exists(p):
                conf = cls.from_yaml(p)
                conf.load()
                logger.info("Config loaded: %s", p)
                matched = True
                break
        if not matched:
            logger.warning("No config file found, using default config")
            conf.load()
        return conf

    def replace(self, other: TBaseConfig) -> None:
        self._set_conf(other)

    def dump(self, destpath: str = "") -> str:
        dump = yaml.dump(self.conf.model_dump())
        if destpath:
            with open(destpath, "w", encoding="utf-8") as file:
                file.write(dump)
        return dump


TConfigSchema = TypeVar("TConfigSchema", bound=ConfigSchema)  # pylint: disable= invalid-name


class Config(Generic[TConfigSchema], GenericConfig[TConfigSchema]):
    __config_class__: type[TConfigSchema]

    @property
    def logging(self) -> LoggingConfigSchema:
        return self.conf.logging

    @property
    def server(self) -> FastAPIConfigSchema:
        return self.conf.server

    @property
    def sentry(self) -> SentryConfigSchema:
        return self.conf.sentry

    @property
    def app(self) -> AppConfigSchema:
        return self.conf.app

    @property
    def name(self) -> str:
        return self.conf.name


T = TypeVar("T", bound=GenericConfig)


# Singleton to get the Configuration instance
# pylint: disable=super-init-not-called
class GConfig(Generic[T]):
    __instance__: T | None = None
    __conf_class__: type[T] | None = None

    def __init__(self, path: str | None = None):
        self.path = path

    def __new__(cls, path: str | None = None) -> T:
        if cls.__instance__ is None:
            if cls.__conf_class__ is None:
                raise ValueError("conf_class not set")
            cls.__instance__ = cls.__conf_class__.auto_config(path)
        return cls.__instance__

    @classmethod
    def reinit(cls) -> None:
        cls.__instance__ = None

    @classmethod
    def set_conf_class(cls, conf_class: type[T]) -> None:
        cls.__conf_class__ = conf_class

    @classmethod
    def instance(cls) -> T:
        if cls.__instance__ is None:
            raise ValueError("Instance not initialized")
        return cls.__instance__


def config(path: str | None = None, confclass: type[T] = Config, reload: bool = False) -> T:
    if confclass is not None:
        GConfig[confclass].set_conf_class(confclass)
    if reload:
        GConfig[confclass].reinit()
    # load the configuration
    _ = GConfig[confclass](path)
    return GConfig[confclass].instance()

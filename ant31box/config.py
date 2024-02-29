# pylint: disable=no-self-argument

import json
import logging
import logging.config
import os
from typing import Any, Generic, Type, TypeVar

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

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
    name: str = Field(default="ant31box-defau")
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


# Main configuration schema
class ConfigSchema(BaseSettings):
    model_config = SettingsConfigDict(env_prefix=f"{ENVPREFIX}_", env_nested_delimiter="__", case_sensitive=False)
    app: AppConfigSchema = Field(default_factory=AppConfigSchema)
    logging: LoggingConfigSchema = Field(default_factory=LoggingConfigSchema)
    server: FastAPIConfigSchema = Field(default_factory=FastAPIConfigSchema)
    sentry: SentryConfigSchema = Field(default_factory=SentryConfigSchema)


TConfigSchema = TypeVar("TConfigSchema", bound=ConfigSchema)  # pylint: disable= invalid-name


class Config(Generic[TConfigSchema]):
    _env_prefix = ENVPREFIX

    def __init__(self, conf: TConfigSchema):
        self.loaded = False
        self._conf: TConfigSchema = conf
        self._set_conf(conf)

    @property
    def conf(self) -> TConfigSchema:
        return self._conf

    def _set_conf(self, conf: TConfigSchema) -> None:
        self._conf = conf
        self.load(force=True)

    @property
    def logging(self) -> LoggingConfigSchema:
        return self.conf.logging

    @property
    def server(self) -> FastAPIConfigSchema:
        return self.conf.server

    @property
    def sentry(self) -> SentryConfigSchema:
        return self.conf.sentry

    def __getattr__(self, name: str) -> Any:
        return getattr(self.conf, name)

    @property
    def app(self) -> AppConfigSchema:
        return self.conf.app

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
                    and not self.app.name in loaded_config["loggers"]
                    and "ant31box" in loaded_config["loggers"]
                ):
                    loaded_config["loggers"][self.app.name] = loaded_config["loggers"]["ant31box"]
                logging.config.dictConfig(loaded_config)

        if log_level is not None:
            if isinstance(log_level, str):
                log_level = LOG_LEVELS[log_level.lower()]
            logging.getLogger(self.app.name).setLevel(log_level)
            logging.getLogger("ant31box").setLevel(log_level)
            logging.getLogger("root").setLevel(log_level)

    @classmethod
    def from_yaml(cls, file_path: str) -> "Config":
        with open(file_path, "r", encoding="utf-8") as file:
            config_dict = yaml.safe_load(file)
        return cls(ConfigSchema.model_validate(config_dict))

    @classmethod
    def default_config(cls) -> "Config":
        return cls(ConfigSchema())

    @classmethod
    def auto_config(cls, path: str | None = None) -> "Config":
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

    def replace(self, other: TConfigSchema) -> None:
        self._set_conf(other)

    def dump(self, destpath: str = "") -> str:
        dump = yaml.dump(self.conf.model_dump())
        if destpath:
            with open(destpath, "w", encoding="utf-8") as file:
                file.write(dump)
        return dump


T = TypeVar("T", bound=Config)


# Singleton to get the Configuration instance
# pylint: disable=super-init-not-called
class GConfig(Generic[T]):
    __instance__: T | None = None
    __conf_class: Type[T]

    def __init__(self, path: str | None = None):
        self.path = path

    def __new__(cls, path: str | None = None) -> T:
        if cls.__instance__ is None:
            cls.__instance__ = cls.__conf_class.auto_config(path)
        return cls.__instance__

    @classmethod
    def reinit(cls) -> None:
        cls.__instance__ = None

    @classmethod
    def set_conf_class(cls, conf_class: Type[T]) -> None:
        cls.__conf_class = conf_class


def config(path: str | None = None, confclass: Type[T] = Config, reload: bool = False) -> T:
    if confclass is not None:
        GConfig[confclass].set_conf_class(confclass)
    if reload:
        GConfig[confclass].reinit()
    return GConfig(path)

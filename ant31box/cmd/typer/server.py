# pylint: disable=too-many-arguments

import enum
import logging
from typing import Annotated

import typer
import uvicorn

from ant31box.config import Config
from ant31box.config import config as confload
from ant31box.init import init_from_config

app = typer.Typer()

logger = logging.getLogger("ant31box.info")


class LogLevel(str, enum.Enum):
    critical = "critical"
    error = "error"
    warning = "warning"
    info = "info"
    debug = "debug"


def run_server(config: Config):
    logger.info("Starting server")
    typer.echo(f"{config.server.model_dump()}")
    init_from_config(config, "fastapi")
    uvicorn.run(
        config.server.server,
        host=config.server.host,
        port=config.server.port,
        log_level=config.logging.level,
        # log_config=config.logging.log_config,
        use_colors=config.logging.use_colors,
        reload=config.server.reload,
        factory=True,
    )


@app.command(context_settings={"auto_envvar_prefix": "FASTAPI"})
def server(
    config: Annotated[
        str | None,
        typer.Option(
            "--config",
            "-c",
            exists=True,
            help="Configuration file in YAML format.",
            show_default=True,
            envvar="FASTAPI_CONFIG",
        ),
    ] = None,
    host: Annotated[
        str | None,
        typer.Option(
            "--host",
            help="Address of the server",
            show_default=True,
            envvar="FASTAPI_HOST",
        ),
    ] = None,
    port: Annotated[int | None, typer.Option("--port", help="Port to listen on", envvar="FASTAPI_PORT")] = None,
    log_config: Annotated[
        str | None,
        typer.Option(
            "--log-config",
            exists=True,
            help="Logging configuration file. Supported formats: .ini, .json, .yaml.",
            show_default=True,
            envvar="FASTAPI_LOG_CONFIG",
        ),
    ] = None,
    log_level: Annotated[
        LogLevel,
        typer.Option(
            "--log-level",
            help="Log level.",
            show_default=True,
            case_sensitive=False,
            envvar="FASTAPI_LOG_LEVEL",
        ),
    ] = LogLevel.info,
    use_colors: Annotated[
        bool,
        typer.Option(
            "--use-colors/--no-use-colors",
            help="Enable/Disable colorized logging.",
            envvar="FASTAPI_USE_COLORS",
        ),
    ] = True,
) -> None:
    """Starts the server."""
    _config = confload(config)
    if host:
        _config.server.host = host
    if port:
        _config.server.port = port
    if log_level:
        _config.logging.level = log_level.value
    if log_config:
        _config.logging.log_config = log_config
    if use_colors is not None:
        _config.logging.use_colors = use_colors

    run_server(_config)

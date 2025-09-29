#!/usr/bin/env python3

import pathlib

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from ant31box.config import Config, ConfigSchema, SentryConfigSchema


def init_sentry(config: SentryConfigSchema, integration_app: str = ""):
    if config.dsn:
        integrations = []
        if integration_app == "fastapi":
            integrations = [
                StarletteIntegration(),
                FastApiIntegration(),
            ]
        sentry_sdk.init(  # pylint: disable=abstract-class-instantiated
            dsn=config.dsn,
            integrations=integrations,
            traces_sample_rate=config.traces_sample_rate,
            environment=config.environment,
        )


def _create_tmp_dir(promdir: str) -> None:
    pathlib.Path(promdir).mkdir(parents=True, exist_ok=True)


def init(config: ConfigSchema, app: str = "fastapi"):
    _create_tmp_dir(config.app.prometheus_dir)
    init_sentry(config.sentry, app)


def init_from_config(config: Config, app: str = "fastapi"):
    """
    Initialize the application from a Config object.
    This is the recommended way for initialization.
    """
    _create_tmp_dir(config.app.prometheus_dir)
    init_sentry(config.sentry, app)

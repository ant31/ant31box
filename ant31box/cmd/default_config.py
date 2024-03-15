import click
import yaml

from ant31box.config import LOGGING_CONFIG, LoggingConfigSchema, config


@click.command()
def default_config() -> None:
    conf = config()
    conf.conf.logging = LoggingConfigSchema(log_config=LOGGING_CONFIG)
    click.echo(yaml.dump(conf.conf.model_dump(), default_flow_style=False))

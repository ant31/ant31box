import click
import yaml

from ant31box.config import LOGGING_CONFIG, ConfigSchema, LoggingConfigSchema


@click.command()
def default_config() -> None:
    config = ConfigSchema(logging=LoggingConfigSchema(log_config=LOGGING_CONFIG))
    click.echo(yaml.dump(config.model_dump(), default_flow_style=False))

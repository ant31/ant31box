import typer
import yaml

from ant31box.config import LOGGING_CONFIG, LoggingConfigSchema, config

app = typer.Typer()


@app.command()
def default_config() -> None:
    """Shows the default configuration."""
    conf = config()
    conf.conf.logging = LoggingConfigSchema(log_config=LOGGING_CONFIG)
    typer.echo(yaml.dump(conf.conf.model_dump(), default_flow_style=False))

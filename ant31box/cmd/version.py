import json

import click

from ant31box.version import VERSION, Version


@click.command()
@click.option("--output", "-o", default="json", type=click.Choice(["json", "text"]))
@click.pass_context
def version(ctx: click.Context, output: str, ver: Version = VERSION) -> None:
    if output == "json":
        click.echo(json.dumps(ver.to_dict(), indent=2))
    else:
        click.echo(ver.text())
    ctx.exit()

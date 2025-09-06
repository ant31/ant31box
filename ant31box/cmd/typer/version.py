import json
from typing import Annotated

import typer
from rich.pretty import pprint

from ant31box.version import VERSION

from .models import OutputEnum

app = typer.Typer()


@app.command()
def version(
    output: Annotated[
        OutputEnum,
        typer.Option("--output", "-o", help="Output format."),
    ] = OutputEnum.json,
) -> None:
    """Displays the version of the application."""
    ver = VERSION
    if output == "json":
        print(json.dumps(ver.to_dict(), indent=2))
    else:
        pprint(ver.text())
    raise typer.Exit()

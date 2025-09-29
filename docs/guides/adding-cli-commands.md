# Guide: Adding CLI Commands

`ant31box` uses [`typer`](https://typer.tiangolo.com/) to build its command-line interface. You can easily extend the default CLI with your own commands and command groups.

## Step 1: Create the Command File

First, create a new Python file for your commands. For example, `my_app/cli.py`.

```python
# my_app/cli.py
from typing import Annotated
import typer

# It's common to create a typer "sub-application" for a group of related commands
app = typer.Typer(help="Custom commands for my application.")

@app.command()
def hello(
    name: Annotated[
        str,
        typer.Option("--name", "-n", help="The name to greet."),
    ] = "World",
    config_path: Annotated[
        str | None,
        typer.Option("--config", "-c", help="Path to config file."),
    ] = None,
) -> None:
    """
    A simple command that greets the user and loads configuration.
    """
    # Adhere to the DI pattern by loading config explicitly
    from ant31box.config import config
    conf = config(path=config_path)

    typer.echo(f"Hello, {name} from env: {conf.app.env}!")

@app.command()
def goodbye(
    name: Annotated[str, typer.Argument(help="The name to say goodbye to.")]
):
    """
    Says goodbye.
    """
    typer.echo(f"Goodbye, {name}!")
```

-   `@app.command()`: This decorator turns a function into a command-line command.
-   `typer.Option(...)`: Defines a command-line option (e.g., `--name`).
-   `typer.Argument(...)`: Defines a positional command-line argument.
-   The function's docstring is automatically used as the help text for the command.

## Step 2: Create a Main Entry Point

Create a file `run.py` in your project root to assemble your CLI. This file will import the commands from `ant31box` and add your own.

```python
#!/usr/bin/env python3
import typer

# Import command groups from ant31box
from ant31box.cmd.typer.server import app as server_app
from ant31box.cmd.typer.version import app as version_app
from ant31box.cmd.typer.default_config import app as config_app

# Import your custom command app
from my_app.cli import app as my_app_cli

# Create a new top-level Typer app
app = typer.Typer(no_args_is_help=True)

# Add the ant31box commands
app.add_typer(server_app, name="server")
app.add_typer(version_app, name="version")
app.add_typer(config_app, name="default-config")

# Add your app as a subcommand
app.add_typer(my_app_cli, name="my-app")

def main():
    app()

if __name__ == "__main__":
    main()
```

## Step 3: Update Project Entry Point

In your `pyproject.toml`, point the script entry point to your new `run:main` function.

```toml
# in pyproject.toml
[project.scripts]
my-cli = "run:main"
```

## Step 4: Verify Your Command

You can now verify your command from your terminal after installing your project.

```bash
# See the new "my-app" command group listed
my-cli --help

# See your new commands
my-cli my-app --help

# Run the command
my-cli my-app hello --name "Developer"
```

Output:
```
Hello, Developer!
```

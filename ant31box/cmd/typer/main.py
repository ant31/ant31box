import typer

from .default_config import app as default_config_app
from .server import app as server_app
from .version import app as version_app


def main() -> None:
    app = typer.Typer(no_args_is_help=True)
    app.add_typer(default_config_app)
    app.add_typer(server_app)
    app.add_typer(version_app)

    # Parse cmd-line arguments and options
    # pylint: disable=no-value-for-parameter
    app()


if __name__ == "__main__":
    main()

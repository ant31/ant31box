import asyncio
import logging
from typing import Annotated

import typer

from ant31box.config import Config
from ant31box.config import config as confload
from ant31box.db import get_engine
from ant31box.importer import import_from_string

app = typer.Typer(help="Database seeding commands.")
logger = logging.getLogger(__name__)


@app.command()
def db(
    config: Annotated[
        str | None,
        typer.Option(
            "--config",
            "-c",
            exists=True,
            help="Configuration file in YAML format.",
            show_default=True,
        ),
    ] = None,
) -> None:
    """
    Initializes and seeds the database with default data.

    This command uses the 'seeder' import string defined in your application's
    configuration to locate and run your seeding function.
    """
    _config = confload(config)

    seeder_path = _config.app.seeder
    if not seeder_path:
        typer.echo(typer.style("Error: 'app.seeder' path is not defined in the configuration.", fg=typer.colors.RED))
        raise typer.Exit(1)

    typer.echo(f"Running seeder from: {seeder_path}")

    try:
        # Dynamically import the seeder function
        seeder_func = import_from_string(seeder_path)

        asyncio.run(run_seeder(seeder_func, _config))

        typer.echo(typer.style("Database seeding completed successfully.", fg=typer.colors.GREEN))

    except ImportError as e:
        typer.echo(typer.style(f"Error importing seeder: {e}", fg=typer.colors.RED), err=True)
        raise typer.Exit(1) from e
    except Exception as e:
        logger.error(f"Database seeding failed: {e}", exc_info=True)
        typer.echo(typer.style(f"Error: Database seeding failed. {e}", fg=typer.colors.RED), err=True)
        raise typer.Exit(1) from e


async def run_seeder(seeder_func, conf: Config):
    """
    Helper to set up the database engine and session for the seeder.
    """
    if get_engine is None:
        typer.echo(
            typer.style(
                "Database components not found. Please install 'achemy' for database functionality.",
                fg=typer.colors.RED,
            ),
            err=True,
        )
        raise typer.Exit(1)

    engine = get_engine(conf)
    _, session_factory = engine.session()

    async with session_factory() as session:
        # The seeder function is expected to be async and accept a session
        await seeder_func(session)
        await session.commit()

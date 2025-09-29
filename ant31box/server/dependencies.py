from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency to create and clean up a database session per request.
    This requires that the database engine and session factory have been initialized
    and attached to the app state, for example, via the server's lifespan manager.

    Raises:
        AttributeError: If the session factory is not found in the app state.

    Yields:
        An active SQLAlchemy AsyncSession.
    """
    session_factory = request.app.state.session_factory
    if not session_factory:
        raise AttributeError("session_factory not found in app state. Is the database engine initialized?")

    async with session_factory() as session:
        yield session

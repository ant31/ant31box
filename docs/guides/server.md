# Guide: Creating a FastAPI Server

`ant31box` provides a pre-configured, production-ready FastAPI server that you can easily extend with your own application logic.

## Core Concepts

-   **`serve()` function**: The main entry point for creating the FastAPI application instance. It takes a `Config` object and sets up all the configured middlewares and routers.
-   **`Server` Class**: The underlying class that builds the `FastAPI` app. You can subclass this for advanced customization.
-   **Routers**: Standard FastAPI `APIRouter` instances that contain your application's endpoints.
-   **Middlewares**: Functions that process requests and responses. `ant31box` includes middlewares for error handling, Prometheus metrics, CORS, and more.

## Quickstart: Adding Your Endpoints

The easiest way to build your application is to create your own routers and add them to the configuration.

**1. Create a file for your API, e.g., `my_app/api.py`:**

```python
from fastapi import APIRouter

# Create a new router
router = APIRouter(prefix="/greeting", tags=["Greeting"])

@router.get("/{name}")
async def get_greeting(name: str):
    """Returns a personalized greeting."""
    return {"message": f"Hello, {name}!"}
```

**2. Update your configuration to load the new router:**

In your `config.yaml`, add the import string for your router to the `server.routers` list.

```yaml
# in config.yaml
server:
  host: 0.0.0.0
  port: 8000
  routers:
    - "my_app.api:router" # Add this line
```

**3. Create the server:**

In your application entry point (`main.py`), load the configuration and call `serve()`.

```python
# main.py
from ant31box.config import config
from ant31box.server.server import serve

def main():
    # Load configuration once at the application's entry point
    conf = config()

    # Pass the configuration object to the serve function
    return serve(conf=conf)

# The `app` object needs to be available at the module level for Uvicorn
app = main()

# To run with the ant31box CLI:
# ant31box server --config config.yaml
```

**4. Run the server:**

```bash
ant31box server --config config.yaml
```
Your new endpoint is now live at `http://127.0.0.1:8000/greeting/world`.

## Customizing Middlewares

You can add, replace, or remove middlewares via the configuration. `ant31box` comes with a set of default middlewares: `catchExceptions`, `prometheus`, `proxyHeaders`, and `addProcessTimeHeader`.

-   **Add a middleware**: Add its name to the `server.middlewares` list in `config.yaml`.
-   **Replace the defaults**: Define `server.middlewares_replace_default` with a new list of middlewares to use instead of the defaults.

For a full list of available middlewares, see the `AVAILABLE_MIDDLEWARES` dictionary in `ant31box/server/server.py`.

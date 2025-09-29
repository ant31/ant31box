# ant31box

`ant31box` is a powerful, asynchronous Python toolkit for bootstrapping modern microservices. It provides a production-ready foundation for your applications with a pre-configured FastAPI server, robust configuration management, and essential utilities for interacting with services like S3.

## Key Features

-   **Production-Ready FastAPI Server**: Start your project with a secure and observable FastAPI application, complete with middlewares for CORS, Prometheus metrics, error handling, and token authentication.
-   **Type-Safe Configuration**: Manage your application's settings with Pydantic V2, loading from YAML files and environment variables with a clear hierarchy.
-   **Fully Asynchronous Clients**: Built from the ground up with `async/await`, including a powerful `DownloadClient` for handling files from HTTP, S3, and local storage, and a dedicated `S3Client` powered by `aioboto3`.
-   **Extensible and Opinionated**: Designed to be easily extended. Add your own API routers, middlewares, and configuration schemas with minimal boilerplate.
-   **Modern CLI with Typer**: A clean, modern command-line interface for common tasks like running the server and managing configuration.

## Getting Started

### Installation

Install the library and its dependencies. For development, include the `dev` and `s3` extras.

```bash
pip install "ant31box[all]"

# Or for development
pip install -e ".[dev,s3]"
```

*(Requires Python >= 3.12)*

### Quickstart: Your First Microservice

Let's build a simple "Greeting Service".

**1. Project Structure**

Create the following directory structure for your project.

```
my-greeting-service/
├── src/
│   └── greeter/
│       ├── __init__.py
│       └── api.py
├── config.yaml
└── run.py
```

**2. Create your API Endpoint**

**File: `src/greeter/api.py`**
```python
from fastapi import APIRouter

router = APIRouter(prefix="/greeting", tags=["Greeting"])

@router.get("/{name}")
async def get_greeting(name: str):
    """Returns a personalized greeting."""
    return {"message": f"Hello, {name}!"}
```

**3. Create `config.yaml`**

Generate the default configuration and add your new API router to it.

```bash
ant31box default-config > config.yaml
```

Now, open `config.yaml` and add your router to the `server.routers` list:
```yaml
# in config.yaml
server:
  # ... other server settings
  routers:
    - "greeter.api:router"
```

**4. Create the Application Entry Point**

**File: `run.py`**
```python
#!/usr/bin/env python3
from ant31box.config import config
from ant31box.server.server import serve

def main():
    """Application entry point."""
    conf = config()
    return serve(conf=conf)

# This makes the `app` object discoverable for ASGI servers like Uvicorn
app = main()
```

**5. Run the Server**

From your project root, run the server using the `ant31box` CLI.

```bash
# Add your source code to the PYTHONPATH
export PYTHONPATH=$PYTHONPATH:./src

# Run the server
ant31box server --config config.yaml
```
Your new endpoint is now available at `http://localhost:8080/greeting/world`.

## Full Documentation

For detailed guides, tutorials, and the API reference, please visit the **[full documentation site](https://ant31.github.io/ant31box)**.

## Development

-   **Setup:** `pip install -e .[dev,s3]`
-   **Testing:** `make test`
-   **Linting & Formatting:** `make check` and `make fix`

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.

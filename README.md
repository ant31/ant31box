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

Create a `main.py` and a `config.yaml` to launch your first application.

**1. Create `config.yaml`:**

Start with the default configuration.

```bash
ant31box default-config > config.yaml
```
You can customize your server port, logging levels, and other settings in this file.

**2. Create `main.py`:**

```python
from fastapi import APIRouter
from ant31box.config import config
from ant31box.server.server import serve

# 1. Define a new API router for your application's endpoints
custom_router = APIRouter(prefix="/my-app", tags=["Custom"])

@custom_router.get("/hello")
async def hello_world():
    return {"message": "Hello from ant31box!"}

# 2. Load the application configuration
conf = config()

# 3. Add your custom router to the server configuration
conf.server.routers.append("main:custom_router")

# 4. Create the FastAPI app
# The serve function builds the app with all pre-configured middlewares
app = serve(conf=conf)

# To run this app: uvicorn main:app --reload
```

**3. Run the Server:**

You can use the built-in CLI to run the server, which will automatically pick up your configuration.

```bash
ant31box server --config config.yaml --reload
```
Your new endpoint is now available at `http://localhost:8080/my-app/hello`.

## Full Documentation

For detailed guides, tutorials, and the API reference, please visit our **[full documentation site](https://ant31.github.io/ant31box)**.

-   **[Introduction](./docs/introduction/what-is-ant31box.md)**: Learn about the core philosophy.
-   **[Configuration Guide](./docs/guides/configuration.md)**: Master the configuration system.
-   **[Creating a Server](./docs/guides/server.md)**: Deep dive into the FastAPI server.
-   **[Using the S3 Client](./docs/guides/s3-client.md)**: Guide to asynchronous S3 operations.

## Development

-   **Setup:** `pip install -e .[dev,s3]`
-   **Testing:** `make test`
-   **Linting & Formatting:** `make check` and `make fix`

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.

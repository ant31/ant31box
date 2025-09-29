# Key Features

`ant31box` is packed with features designed to make building and deploying microservices as seamless as possible.

-   **Production-Ready FastAPI Server**: With `FastAPI` integration, you get a high-performance API server out-of-the-box. It comes pre-configured with essential middlewares for CORS, Prometheus metrics, graceful error handling, process timing, and token-based authentication.

-   **Type-Safe & Flexible Configuration**: Manage settings for your application, server, and clients in one place. The system, built on Pydantic V2, loads configuration from YAML files and environment variables, providing validation, clear defaults, and a simple hierarchy.

-   **Fully Asynchronous I/O**: The entire library is built with `async/await`, ensuring your application remains non-blocking and efficient. This includes an `S3Client` powered by `aioboto3` and a `DownloadClient` for handling files over HTTP, S3, or the local filesystem.

-   **Dependency Injection Pattern**: `ant31box` encourages a clean architecture by promoting dependency injection for configuration and clients, making your code more modular, easier to test, and less reliant on global state.

-   **Modern CLI with Typer**: A pre-built command-line interface using `typer` provides essential commands for running the server, inspecting the version, and dumping the default configuration, and it's easy to extend with your own commands.

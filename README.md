# ant31box

`ant31box` is a Python library providing a collection of utilities, including:

*   **Configuration Management:** Load configuration from YAML files and environment variables using Pydantic models.
*   **FastAPI Server:** A pre-configured FastAPI server setup with common middlewares (CORS, Prometheus, error handling, token auth) and extensible routing.
*   **S3 Client:** Utilities for interacting with S3-compatible storage.
*   **Async HTTP Client:** Base client built on `aiohttp` and a specialized client for downloading files from various sources (HTTP, S3, local).
*   **Command-Line Interface:** Built with `click` for common tasks like running the server, showing version info, and dumping default configuration.
*   **Logging:** Configurable logging setup with colorized output.

## Installation

```bash
pip install .
# Or for development
pip install -e .[dev,s3] # Include extras like s3 if needed
```

*(Requires Python >= 3.11)*

## Usage

### Command-Line Interface (CLI)

The package provides a CLI tool, typically accessed via `ant31box` (as defined in `pyproject.toml`).

**Run the FastAPI Server:**

```bash
ant31box server --config config.yaml --port 8000
```

*   Use `--config` or the `ANT31BOX_CONFIG` environment variable to specify a configuration file.
*   See `ant31box server --help` for more options.

**Show Version Information:**

```bash
ant31box version
ant31box version --output text
```

**Show Default Configuration:**

```bash
ant31box default-config > default_config.yaml
```

### Library Usage

**Configuration:**

```python
from pydantic import Field
from ant31box.config import config, ConfigSchema, Config, S3ConfigSchema

# Define your custom config schema inheriting from ConfigSchema if needed
class MyAppConfigSchema(ConfigSchema):
    my_setting: str = Field(default="default_value")
    s3: S3ConfigSchema = Field(default_factory=S3ConfigSchema) # Add S3 config if needed

class MyAppConfig(Config[MyAppConfigSchema]):
     __config_class__ = MyAppConfigSchema

# Load configuration (searches for localconfig.yaml, config.yaml by default)
# Set the custom config class before first call to config()
conf: MyAppConfig = config(confclass=MyAppConfig)

# Access configuration values
print(conf.server.host)
print(conf.conf.my_setting) # Access custom setting
print(conf.conf.s3.bucket) # Access S3 setting
```

**File Download Client:**

```python
import asyncio
from ant31box.client.filedl import DownloadClient
from ant31box.config import S3ConfigSchema

async def main():
    # Configure S3 if needed
    s3_conf = S3ConfigSchema(bucket="my-bucket", region="eu-west-1") # Add credentials if needed
    client = DownloadClient(s3_config=s3_conf)

    # Download from HTTP
    http_info = await client.download("https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png", dest_dir="/tmp")
    print(f"Downloaded HTTP file to: {http_info.path}")

    # Download from local file (effectively copies)
    # Create a dummy source file first
    with open("/tmp/source.txt", "w") as f:
        f.write("hello world")
    local_info = await client.download("file:///tmp/source.txt", dest_dir="/tmp", output="/tmp/dest.txt")
    print(f"Copied local file to: {local_info.path}")

    # Download from S3 (requires S3 config and moto/boto3 for testing or real credentials)
    # Ensure your S3 bucket and file exist, or mock them with moto
    # try:
    #     s3_info = await client.download("s3://my-bucket/data/file.csv", dest_dir="/tmp")
    #     print(f"Downloaded S3 file to: {s3_info.path}")
    # except Exception as e:
    #     print(f"Could not download from S3 (ensure bucket/file exist or use moto): {e}")


asyncio.run(main())
```

**S3 Client:**

```python
from ant31box.config import S3ConfigSchema
from ant31box.s3 import S3Client

s3_conf = S3ConfigSchema(
    bucket="your-bucket",
    # access_key="...", # Optional: Reads from env/AWS config by default
    # secret_key="..."  # Optional: Reads from env/AWS config by default
    # endpoint_url="http://localhost:5000", # Optional: for localstack/minio
    # region="us-east-1", # Optional
)

s3_client = S3Client(s3_conf)

# Upload a file (ensure bucket exists or use mocking)
# try:
#     with open("/tmp/upload_me.txt", "w") as f:
#         f.write("upload test")
#     s3_dest = s3_client.upload_file("/tmp/upload_me.txt", dest="remote/path/file.txt")
#     print(f"Uploaded to: {s3_dest.url}")
#
#     # Download a file
#     s3_client.download_file(s3_dest, "/tmp/downloaded_file.txt")
#     print("File downloaded.")
# except Exception as e:
#     print(f"S3 operation failed (ensure bucket exists or use moto): {e}")

```

## Configuration

Configuration is managed via `ant31box.config`.

*   **Sources:** Configuration is loaded from environment variables (prefixed with `ANT31BOX_`, nested with `__`) and YAML files. Environment variables take precedence.
*   **Default Files:** `localconfig.yaml`, `config.yaml`. Specify a different file using the `ANT31BOX_CONFIG` environment variable or the `--config` CLI option.
*   **Schema:** Configuration structure is defined by `ant31box.config.ConfigSchema` (and potentially subclasses) using Pydantic V2.
*   **Dumping Default:** Use `ant31box default-config` to see the default structure and values.

Key configuration sections (defined in `ConfigSchema`):

*   `app`: General application settings (e.g., `env`, `prometheus_dir`).
*   `logging`: Logging setup (`level`, `use_colors`, `log_config`).
*   `server`: FastAPI server settings (`host`, `port`, `middlewares`, `routers`, `cors`, `token_auth`).
*   `sentry`: Sentry integration settings (`dsn`, `environment`).
*   `name`: Application name.

**Note:** `S3ConfigSchema` is *not* part of the default `ConfigSchema`. If you need global S3 settings loaded from the main config file, you must include it in a custom `ConfigSchema` subclass, as shown in the usage example. Otherwise, instantiate `S3ConfigSchema` directly where needed.

## Features

*   **Async Support:** Leverages `asyncio`, `aiohttp`, `aiofiles` for non-blocking I/O.
*   **Pydantic Integration:** Strong typing and validation (Pydantic V2) for configuration and models.
*   **Extensible Server:** Easily add custom FastAPI routers and middlewares. See `ant31box.server.server.Server` class variables (`_default_middlewares`, `_available_middlewares`, etc.).
*   **File Handling:** Unified interface (`DownloadClient`) for downloading files from HTTP(S), S3, and local paths.
*   **S3 Utilities:** Direct S3 operations (upload, download, copy). Requires `boto3` (`pip install ant31box[s3]`).
*   **Standardized CLI:** Common commands for server management and inspection using `click`.

## Development

*   **Setup:** `pip install -e .[dev,s3]`
*   **Testing:** `make test` (uses `pytest`)
*   **Linting/Formatting:** `make lint` (uses `ruff`, `black`, `isort`, `pyright`)


## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.

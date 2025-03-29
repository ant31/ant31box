# Client Wrapper Documentation

The `ant31box` client wrapper provides a high-level interface around `aiohttp` for downloading files from various sources (local files, HTTP/HTTPS URLs, and S3). It is built on top of the `BaseClient` (in `ant31box/client/base.py`) and extended in `DownloadClient` (in `ant31box/client/filedl.py`).

## Importing the Client

You can either import the `DownloadClient` directly:

```python
from ant31box.client.filedl import DownloadClient
```

Or use the cached version from the clients module:

```python
from ant31box.clients import filedl_client

client = filedl_client()  # Returns a cached DownloadClient instance
```

## Instantiating the Client

### Basic Use (without S3)

For regular use (e.g. downloading via HTTP or from local file system):

```python
client = DownloadClient()
```

### S3 Support

If you need S3 support, configure an S3 client as follows:

```python
from ant31box.config import S3ConfigSchema
from ant31box.client.filedl import DownloadClient

s3_config = S3ConfigSchema(
    bucket="your-bucket-name",
    prefix="optional/prefix/",
    # ... set additional S3 configuration as required
)

client = DownloadClient(s3_config=s3_config)
```

## Usage Examples

### Downloading a File over HTTP/HTTPS

The `download` method detects the scheme and performs an HTTP GET. Example:

```python
import asyncio

async def download_http_example():
    client = DownloadClient()
    url = "https://example.com/path/to/file.txt"
    # Optionally specify a destination directory or output path
    file_info = await client.download(source=url, dest_dir="/tmp")
    
    print("Downloaded file:", file_info.filename)
    print("Stored at:", file_info.path)

asyncio.run(download_http_example())
```

### Downloading a Local File

Use the same `download` method with a file URL (or file path with an empty scheme):

```python
import asyncio

async def download_local_example():
    client = DownloadClient()
    local_url = "file:///path/to/localfile.txt"  # or simply "file:///..."
    file_info = await client.download(source=local_url, dest_dir="/tmp")
    
    print("Copied file:", file_info.filename)
    print("Stored at:", file_info.path)

asyncio.run(download_local_example())
```

### Downloading from S3

Once the S3 client is set up (see the S3 Support section), you can download from an S3 URL synchronously. For example:

```python
def download_s3_example():
    from ant31box.config import S3ConfigSchema
    from ant31box.client.filedl import DownloadClient

    s3_config = S3ConfigSchema(
        bucket="your-bucket-name",
        prefix="optional/prefix/",
        # ... additional S3 settings
    )

    client = DownloadClient(s3_config=s3_config)
    s3_url = "s3://your-bucket-name/path/to/file.txt"
    
    file_info = client.download_s3(source=s3_url, dest_dir="/tmp")
    
    print("Downloaded S3 file:", file_info.filename)
    print("Stored at:", file_info.path)

download_s3_example()
```

## Additional Information

- **Client Session Management:**  
  The `BaseClient` automatically creates an `aiohttp.ClientSession` when needed. To properly free resources, call the `close` method when finished:
  ```python
  client = DownloadClient()
  # ... perform downloads
  client.close()
  ```

- **Custom Headers:**  
  The client automatically sets standard headers (such as `Content-Type` and `User-Agent`). You can override or extend these headers by calling the `headers()` method when making requests.

- **Method Overview:**
  - `download(source: str, dest_dir: str | Path = "", output: str | Path | IOBase = "")`  
    A generic method that determines the protocol (`file://`, `http(s)://`, `s3://`) of the source URL and dispatches to the correct download logic.
  
  - `download_file(url: str, source_path: str, dest_dir: str | Path = "", output: str | Path | IOBase = "")`  
    Downloads a file via HTTP/HTTPS, processing the Content-Disposition to determine the filename.

  - `copy_local_file(source_path: str, dest_dir: str | Path = "", output: str | Path | IOBase = "")`  
    Copies a local file.

  - `download_s3(source: str, dest_dir: str | Path = "", output: str | Path | IOBase = "")`  
    Downloads a file from S3. **Note:** This method requires that the S3 client is set via `set_s3()`.

## Conclusion

The ant31box client wrapper simplifies downloading files from various protocols by abstracting the underlying `aiohttp` operations. Whether you are working with local files, HTTP/HTTPS endpoints, or S3, the client provides an intuitive interface to perform downloads with minimal configuration.

Happy coding!

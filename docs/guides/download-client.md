# Guide: Using the Download Client

The `DownloadClient` provides a unified, asynchronous interface for downloading files from various sources, including HTTP(S), Amazon S3, and the local filesystem.

## Creating a Client

To use the `DownloadClient`, you first need an instance. If you plan to download from S3, you must provide an `S3ConfigSchema`.

```python
from ant31box.client.filedl import DownloadClient
from ant31box.config import S3ConfigSchema

# For downloading from HTTP and local files only
http_client = DownloadClient()

# For downloading from S3 as well
s3_conf = S3ConfigSchema(bucket="my-bucket") # Add credentials/region as needed
full_client = DownloadClient(s3_config=s3_conf)
```

A `filedl_client` factory is also available. It's recommended to pass the configuration object to it explicitly.

## Downloading Files

The `download()` method is the single entry point. It automatically detects the source protocol (`http://`, `s3://`, `file://`) and handles the download accordingly. It returns a `FileInfo` Pydantic model containing details about the downloaded file.

### Download from HTTP/HTTPS

```python
from ant31box.config import config

# Load config once
conf = config()

# Create client using dependency injection
client = DownloadClient()


# Download to a specified directory. The original filename is used.
file_info = await client.download(
    source="https://www.python.org/static/community_logos/python-logo-master-v3-TM.png",
    dest_dir="/tmp/downloads"
)

print(f"File downloaded to: {file_info.path}")
# > File downloaded to: /tmp/downloads/python-logo-master-v3-TM.png

# Download to a specific file path
await client.download(
    source="...",
    output="/tmp/my_logo.png"
)

# Download into an in-memory file-like object
from io import BytesIO
buffer = BytesIO()
file_info = await client.download(
    source="...",
    output=buffer
)
buffer.seek(0)
image_data = buffer.read()
print(f"Downloaded {len(image_data)} bytes into memory.")
```

### Download from S3

This requires the client to be configured with S3 settings.

```python
s3_info = await full_client.download(
    source="s3://my-bucket/documents/report.pdf",
    dest_dir="/tmp/reports"
)

print(f"Downloaded S3 file to: {s3_info.path}")
```

### Copy from Local Filesystem

If the source is a local path (with or without the `file://` scheme), the client will copy the file to the destination.

```python
# Create a source file
with open("/tmp/source.txt", "w") as f:
    f.write("hello")

local_info = await http_client.download(
    source="/tmp/source.txt", # or "file:///tmp/source.txt"
    dest_dir="/tmp/copies"
)

print(f"Copied file to: {local_info.path}")
# > Copied file to: /tmp/copies/source.txt
```

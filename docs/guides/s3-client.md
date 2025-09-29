# Guide: Using the S3 Client

`ant31box` includes a fully asynchronous `S3Client` for interacting with AWS S3 or other S3-compatible object storage services. It is built on `aioboto3` to ensure non-blocking I/O operations.

## Configuration

First, you need to configure the S3 client. This is done via the `S3ConfigSchema`. You can instantiate it directly or include it in your main application configuration.

```python
from ant31box.config import S3ConfigSchema

# Direct instantiation
s3_conf = S3ConfigSchema(
    bucket="my-app-bucket",
    region="us-east-1",
    access_key="...", # Can be omitted if using IAM roles or env vars
    secret_key="...", # Can be omitted if using IAM roles or env vars
    endpoint_url="http://localhost:9000", # Optional: for localstack/minio
)
```

If you add `S3ConfigSchema` to your main `ConfigSchema`, these settings can be loaded from your `config.yaml` file.

## Creating a Client

Instantiate `S3Client` with your configuration object.

```python
from ant31box.s3 import S3Client

s3_client = S3Client(s3_conf)
```

## Core Operations

All I/O methods are `async` and must be awaited.

### Uploading a File

The `upload_file_async` method can upload a file from a local path or a file-like object.

```python
import aiofiles

# Upload from a local file path
dest_s3_object = await s3_client.upload_file_async(
    filepath="/path/to/local/file.txt",
    dest="uploads/file.txt" # The key (path) in the S3 bucket
)
print(f"Uploaded to: {dest_s3_object.url}")

# Upload from an in-memory file-like object
from io import BytesIO
file_obj = BytesIO(b"some binary data")
await s3_client.upload_file_async(
    filepath=file_obj,
    dest="uploads/data.bin"
)
```

### Downloading a File

The `download_file_async` method can download an S3 object to a local file path or a file-like object.

```python
from ant31box.models import S3URL

s3_url = S3URL(url="s3://my-app-bucket/uploads/file.txt")

# Download to a local file path
await s3_client.download_file_async(
    s3url=s3_url.to_model(),
    dest="/path/to/save/downloaded_file.txt"
)

# Download to an in-memory BytesIO object
from io import BytesIO
buffer = BytesIO()
await s3_client.download_file_async(
    s3url=s3_url.to_model(),
    dest=buffer
)
buffer.seek(0)
print(buffer.read())
```

### Copying an Object

The `copy_s3_to_s3_async` method copies an object from one S3 location to another, even across different buckets.

```python
src, dest = await s3_client.copy_s3_to_s3_async(
    src_bucket="my-app-bucket",
    src_path="uploads/file.txt",
    dest_bucket="my-app-archive-bucket",
    dest_prefix="archive/2025/"
)

print(f"Copied {src.url} to {dest.url}")
```

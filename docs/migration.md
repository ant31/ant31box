# Migration Guide

This guide outlines the breaking changes, deprecations, and other updates required to migrate your projects to newer versions of `ant31box`.

## Migrating to Version 0.4.0

Version `0.4.0` introduces significant architectural improvements, focusing on dependency injection, true asynchronicity, and optional database integration. While backward compatibility has been maintained, several key components are now deprecated.

### 1. Optional Database Integration (`achemy`)

The new database features require the `achemy` library. If your project uses these features, you must add `achemy` to your dependencies. Projects not using the database layer are unaffected.

### 2. Deprecation of Global `config()`

The global `config()` singleton is now deprecated. The recommended approach is to load your configuration once at your application's entry point and pass the `Config` object explicitly to the functions and classes that require it.

**Old Pattern (Deprecated):**

```python
from ant31box.server.server import serve
from ant31box.clients import filedl_client

# Implicitly uses the global config singleton
app = serve()
client = filedl_client()
```

**New Pattern (Recommended):**

```python
from ant31box.config import config
from ant31box.server.server import serve
from ant31box.clients import filedl_client

def main():
    # Load config once in your application's entry point
    conf = config()

    # Inject the config object
    app = serve(conf=conf)
    client = filedl_client(conf=conf)
    # ...
```

### 2. Deprecation of Synchronous S3 Methods

The `S3Client` methods `upload_file`, `download_file`, and `copy_s3_to_s3` are now deprecated. These methods were wrappers around blocking I/O calls. They have been replaced with truly asynchronous counterparts.

-   `upload_file()` is deprecated. Use `upload_file_async()` instead.
-   `download_file()` is deprecated. Use `download_file_async()` instead.
-   `copy_s3_to_s3()` is deprecated. Use `copy_s3_to_s3_async()` instead.

**Old Pattern (Deprecated):**

```python
# This is a synchronous call under the hood
s3_dest = s3_client.upload_file("/path/to/file.txt")
```

**New Pattern (Recommended):**

```python
# This is a truly asynchronous call
s3_dest = await s3_client.upload_file_async("/path/to/file.txt")
```

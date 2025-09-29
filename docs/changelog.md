# Changelog

All notable changes to this project will be documented in this file.

## [0.4.0] - Unreleased

### Added

-   **Dependency Injection for Configuration**: Components like `serve()`, `DownloadClient`, and CLI commands now accept an optional `Config` object. This is the new recommended pattern, reducing reliance on the global singleton.
-   **Fully Asynchronous S3 Client**: The `S3Client` and `DownloadClient`'s S3 operations have been rewritten using `aioboto3` to be truly non-blocking, improving performance in I/O-bound applications.
-   **New Asynchronous S3 Methods**: Introduced `upload_file_async`, `download_file_async`, and `copy_s3_to_s3_async` for explicit asynchronous S3 operations.

### Changed

-   The minimum required Python version has been updated to `3.12`.

### Deprecated

-   **Global `config()` Singleton**: Using the global `config()` singleton is now deprecated. Please load your configuration once at application startup and pass it to the components that need it.
-   **Synchronous S3 Methods**: The original synchronous methods (`upload_file`, `download_file`, `copy_s3_to_s3`) in `S3Client` are deprecated and will be removed in a future version. Please migrate to the new `_async` suffixed methods.

### Fixed

-   Resolved test failures related to mocking asynchronous AWS calls by integrating `pytest-aioboto3`.

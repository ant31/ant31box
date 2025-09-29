# Concept: Async Everywhere

`ant31box` is designed from the ground up to be **asynchronous**. This is a fundamental architectural choice that allows applications built with the library to be highly performant and scalable, especially for I/O-bound workloads like web servers and API clients.

## What is Asynchronous Programming?

In traditional synchronous programming, when you make a network request (e.g., call an external API or query a database), your program blocks and waits for the response before it can do anything else.

In asynchronous programming, using Python's `async/await` syntax, you can start an I/O operation and then immediately yield control, allowing the program to work on other tasks while it waits for the operation to complete. This is handled by an **event loop**. When the operation is finished, the program resumes where it left off.

This "cooperative multitasking" allows a single process to handle thousands of concurrent connections efficiently, making it ideal for microservices.

## How `ant31box` Uses Async

-   **FastAPI Server**: FastAPI is a high-performance asynchronous web framework. All your API endpoint handlers should be defined as `async def` to take full advantage of this.
-   **HTTP Clients (`BaseClient`)**: The base client is built on `aiohttp`, a powerful asynchronous HTTP client/server library. All network requests made through clients inheriting from `BaseClient` are non-blocking.
-   **S3 Client**: The `S3Client` uses `aioboto3`, the asynchronous version of the standard AWS SDK for Python. This ensures that all interactions with S3 (uploading, downloading, etc.) do not block the event loop.
-   **File I/O**: For file operations, `ant31box` uses libraries like `aiofiles` and `aioshutil` to provide asynchronous alternatives to standard file handling, preventing disk I/O from blocking your application.

## Best Practices for Your Code

When building on top of `ant31box`, you should embrace the asynchronous model:

1.  **Use `async def` for I/O-bound functions**: Any function that performs network calls, database queries, or file system access should be an `async` function. This is especially true for your FastAPI route handlers.
2.  **Use `await` for all coroutine calls**: Whenever you call an `async` function, you must use the `await` keyword. Forgetting to `await` a coroutine is a common mistake and will lead to bugs where the code doesn't execute as expected.
3.  **Avoid blocking calls in `async` functions**: Never use synchronous, blocking libraries (like `requests` or standard `boto3`) inside an `async def` function. A single blocking call can halt the entire event loop, defeating the purpose of using `asyncio`. Always look for an `async`-native library for the task.

By following these principles, you can build highly concurrent and efficient services that fully leverage the power of the `ant31box` toolkit.

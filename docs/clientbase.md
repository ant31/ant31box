# Guide: Creating Custom Clients

The `ant31box.client.base.BaseClient` provides a foundation for creating asynchronous HTTP clients. It handles session management (`aiohttp.ClientSession`), base URL configuration, default headers, and request logging.

## Steps to Create a New Client

1.  **Inherit from `BaseClient`**: Create a new class that inherits from `BaseClient`.
2.  **Initialize the Parent**: Call `super().__init__()` in your class's `__init__` method, providing the base `endpoint` URL for the API and a `client_name`.
3.  **Implement API Methods**: Add `async` methods to interact with specific API endpoints.
    *   Use `self._url("/path/to/endpoint")` to construct the full URL.
    *   Use `self.session` (an `aiohttp.ClientSession` instance) to make requests (e.g., `self.session.get()`).
    *   Use `self.headers()` to get base headers and optionally add or override them.

## Example: A Simple Weather API Client

Let's create a client for a hypothetical weather service.

```python
import logging
from typing import Any
from urllib.parse import urlencode

from ant31box.client.base import BaseClient

logger = logging.getLogger(__name__)

class WeatherApiClient(BaseClient):
    """A client for a hypothetical weather API."""

    def __init__(self, api_key: str, **kwargs: Any) -> None:
        super().__init__(
            endpoint="https://api.weather-service.com/v1",
            client_name="weather-api",
            **kwargs
        )
        self.api_key = api_key

    def headers(self, **kwargs) -> dict[str, str]:
        """Adds the API key to the default headers."""
        extra_headers = {"X-API-Key": self.api_key}
        # Get base headers and update them
        base_headers = super().headers(**kwargs)
        base_headers.update(extra_headers)
        return base_headers

    async def get_current_weather(self, city: str) -> dict[str, Any]:
        """Fetches the current weather for a given city."""
        params = {"city": city}
        request_url = self._url(f"/current?{urlencode(params)}")

        async with self.session.get(request_url, headers=self.headers(), ssl=self.ssl_mode) as resp:
            resp.raise_for_status()
            return await resp.json()

# --- Example Usage ---
async def main():
    api_key = "YOUR_API_KEY"
    if api_key == "YOUR_API_KEY":
        print("Please provide a real API key.")
        return

    client = WeatherApiClient(api_key=api_key)
    try:
        weather = await client.get_current_weather("London")
        print("Current weather in London:", weather)
    finally:
        await client.session.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Key `BaseClient` Features Used

*   **`super().__init__(...)`**: Initializes the base client with the API endpoint and name.
*   **`self._url(path)`**: Constructs the full request URL by joining the base endpoint with the provided path.
*   **`self.session`**: Provides the `aiohttp.ClientSession` instance for making asynchronous requests.
*   **`self.headers()`**: Provides a base set of headers which can be extended in subclasses.

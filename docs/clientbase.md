# Creating Custom Clients with `BaseClient`

The `ant31box.client.base.BaseClient` provides a foundation for creating asynchronous HTTP clients. It handles session management (`aiohttp.ClientSession`), base URL configuration, default headers, and request logging.

## Steps to Create a New Client

1.  **Inherit from `BaseClient`**: Create a new class that inherits from `BaseClient`.
2.  **Initialize the Parent**: Call `super().__init__()` in your class's `__init__` method, providing the base `endpoint` URL for the API and a `client_name`. You can also customize TLS verification and session arguments if needed.
3.  **Implement API Methods**: Add `async` methods to interact with specific API endpoints.
    *   Use `self._url("/path/to/endpoint")` to construct the full URL.
    *   Use `self.session` (an `aiohttp.ClientSession` instance) to make requests (e.g., `self.session.get()`, `self.session.post()`).
    *   Use `self.headers()` to get base headers and optionally add or override headers for specific requests.
    *   Handle request parameters, data payloads, and response processing.

## Example: Google Places API Client

Let's create a simple client to interact with the Google Places API's "Nearby Search" endpoint.

```python
import logging
from typing import Any
from urllib.parse import urlencode

from ant31box.client.base import BaseClient

logger = logging.getLogger(__name__)

class GooglePlacesClient(BaseClient):
    """
    A simple client for the Google Places API.
    """

    def __init__(self, api_key: str, **kwargs: Any) -> None:
        """
        Initializes the Google Places Client.

        Args:
            api_key: Your Google Cloud API key.
            **kwargs: Additional arguments passed to BaseClient.
        """
        # Set the base endpoint for the Google Places API
        super().__init__(
            endpoint="https://maps.googleapis.com/maps/api/place",
            client_name="google-places",
            **kwargs
        )
        self.api_key = api_key
        logger.info("GooglePlacesClient initialized for endpoint: %s", self.endpoint.geturl())

    async def search_nearby(
        self, latitude: float, longitude: float, radius: int, place_type: str | None = None
    ) -> dict[str, Any]:
        """
        Performs a Nearby Search request.

        Args:
            latitude: The latitude around which to retrieve place information.
            longitude: The longitude around which to retrieve place information.
            radius: The distance (in meters) within which to return place results.
            place_type: Restricts the results to places matching the specified type.

        Returns:
            A dictionary containing the API response.

        Raises:
            aiohttp.ClientResponseError: If the API returns an error status.
        """
        path = "/nearbysearch/json"
        params: dict[str, Any] = {
            "location": f"{latitude},{longitude}",
            "radius": radius,
            "key": self.api_key,
        }
        if place_type:
            params["type"] = place_type

        # Construct the full URL using the base endpoint and path
        request_url = self._url(f"{path}?{urlencode(params)}")
        headers = self.headers() # Get default headers

        logger.debug("Requesting Nearby Search: URL=%s", request_url)

        # Use the session from BaseClient to make the GET request
        async with self.session.get(request_url, headers=headers, ssl=self.ssl_mode) as resp:
            # Log request/response details (optional, handled by BaseClient if needed)
            # await self.log_request(resp)

            # Raise an exception for bad status codes (4xx or 5xx)
            resp.raise_for_status()

            # Return the JSON response
            return await resp.json()

# --- Example Usage ---
async def main():
    # Replace with your actual API key
    api_key = "YOUR_GOOGLE_API_KEY"
    if api_key == "YOUR_GOOGLE_API_KEY":
        print("Please replace 'YOUR_GOOGLE_API_KEY' with your actual Google API key.")
        return

    client = GooglePlacesClient(api_key=api_key)

    try:
        # Example: Search for restaurants near Googleplex
        latitude = 37.4220
        longitude = -122.0841
        radius = 1500  # 1.5 km
        place_type = "restaurant"

        print(f"Searching for '{place_type}' near ({latitude}, {longitude}) within {radius}m...")
        results = await client.search_nearby(latitude, longitude, radius, place_type)
        print("API Response:")
        # print(json.dumps(results, indent=2)) # Pretty print results

        if results.get("results"):
             print(f"Found {len(results['results'])} places:")
             for place in results['results'][:5]: # Print first 5
                 print(f"- {place.get('name')} ({place.get('vicinity')})")
        else:
            print(f"No results found. Status: {results.get('status')}")
            if results.get("error_message"):
                print(f"Error: {results.get('error_message')}")


    except Exception as e:
        logger.error("An error occurred: %s", e)
    finally:
        # Important: Close the client session when done
        await client.session.close()
        # Or use client.close() for the sync version if needed outside async context cleanup

if __name__ == "__main__":
    import asyncio
    # Basic logging setup for the example
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("ant31box.client.base").setLevel(logging.DEBUG) # Enable base client debug logs
    asyncio.run(main())

```

## Key `BaseClient` Features Used

*   **`super().__init__(...)`**: Initializes the base client with the API endpoint and name.
*   **`self.endpoint`**: Stores the parsed base URL (`urllib.parse.ParseResult`).
*   **`self._url(path)`**: Constructs the full request URL by joining the base endpoint with the provided path.
*   **`self.session`**: Provides the `aiohttp.ClientSession` instance for making asynchronous requests (`self.session.get`, `self.session.post`, etc.).
*   **`self.headers()`**: Provides a base set of headers (like `User-Agent`) and allows easy customization per request.
*   **`self.ssl_mode`**: Provides the configured TLS verification setting (`True` or `False`) to pass to `aiohttp` requests.
*   **`client.session.close()` / `client.close()`**: Cleans up the underlying `aiohttp` session. It's crucial to close the session when the client is no longer needed, especially in long-running applications or tests.

"""
Generic HTTP client implementation for external service integration.

Provides concrete implementation of HTTP client for making
HTTP requests to external APIs with proper error handling and logging.
"""

import asyncio
from typing import Optional

import aiohttp

from config import config
from core.protocols.base import ApiResponse
from core.utils.logger import get_logger

logger = get_logger()


class HttpClient:
    """
    Generic HTTP client for external API communication.

    Handles HTTP requests with proper error handling,
    timeout management, and logging.
    """

    def __init__(self, base_url: str = None, timeout: int = None):
        """
        Initialize HTTP client.

        Args:
            base_url: Base URL for API endpoints
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or config.api_base_url
        self.timeout = timeout or config.api_timeout
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def request(self, method: str, endpoint: str, **kwargs) -> ApiResponse:
        """
        Make HTTP request with error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for aiohttp request

        Returns:
            ApiResponse with success status and data/error
        """
        session = await self._get_session()
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        try:
            logger.debug(f"Making {method} request to {url}")

            async with session.request(method, url, **kwargs) as response:
                status_code = response.status

                if 200 <= status_code < 300:
                    data = await response.json()
                    logger.debug(f"Successful HTTP response ({status_code}) from {url}")
                    return ApiResponse(success=True, data=data, status_code=status_code)
                elif status_code == 404:
                    logger.info(f"Resource not found (404) from {url}")
                    return ApiResponse(
                        success=False,
                        error="Resource not found",
                        status_code=status_code,
                    )
                else:
                    error_text = await response.text()
                    logger.warning(f"HTTP error {status_code} from {url}: {error_text}")
                    return ApiResponse(
                        success=False,
                        error=f"HTTP error: {status_code}",
                        status_code=status_code,
                    )

        except asyncio.TimeoutError:
            logger.error(f"HTTP request timeout to {url}")
            return ApiResponse(success=False, error="Request timeout")
        except aiohttp.ClientError as e:
            logger.error(f"Network error for {url}: {e}")
            return ApiResponse(success=False, error=f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {e}")
            return ApiResponse(success=False, error=f"Unexpected error: {str(e)}")

    async def get(self, endpoint: str, **kwargs) -> ApiResponse:
        """Make GET request."""
        return await self.request("GET", endpoint, **kwargs)

    async def post(self, endpoint: str, **kwargs) -> ApiResponse:
        """Make POST request."""
        return await self.request("POST", endpoint, **kwargs)

    async def put(self, endpoint: str, **kwargs) -> ApiResponse:
        """Make PUT request."""
        return await self.request("PUT", endpoint, **kwargs)

    async def delete(self, endpoint: str, **kwargs) -> ApiResponse:
        """Make DELETE request."""
        return await self.request("DELETE", endpoint, **kwargs)


# Global HTTP client instance
_http_client: Optional[HttpClient] = None


def get_http_client() -> HttpClient:
    """Get global HTTP client instance."""
    global _http_client
    if _http_client is None:
        _http_client = HttpClient()
    return _http_client


async def close_http_client():
    """Close global HTTP client session."""
    global _http_client
    if _http_client:
        await _http_client.close()
        _http_client = None


__all__ = ["HttpClient", "get_http_client", "close_http_client"]

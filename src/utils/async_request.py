"""
Async HTTP request utilities for OAuth operations.
"""

import logging
from typing import Any, Optional, Dict

try:
    import aiohttp
except ImportError:
    raise ImportError(
        "aiohttp is required for async support. "
        "Install it with: pip install aiohttp"
    )


async def make_async_request(
    method: str,
    url: str,
    params: Any = None,
    headers: Dict[str, str] = None,
    data: Any = None,
    timeout: int = 30
) -> Optional[Dict]:
    """
    Make an async HTTP request.

    Args:
        method: HTTP method (GET, POST, DELETE, etc.)
        url: URL to request
        params: URL parameters
        headers: HTTP headers
        data: Request body data
        timeout: Request timeout in seconds

    Returns:
        dict: JSON response if successful, None otherwise

    Raises:
        aiohttp.ClientError: If request fails
    """
    try:
        timeout_obj = aiohttp.ClientTimeout(total=timeout)

        async with aiohttp.ClientSession(timeout=timeout_obj) as session:
            async with session.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                data=data
            ) as response:
                response.raise_for_status()
                return await response.json()

    except aiohttp.ClientError as e:
        logging.error(f"Async request error: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error in async request: {e}")
        return None

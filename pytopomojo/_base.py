import logging
import os
from typing import Any, Literal, Optional

import requests

from .exceptions import TopomojoException

HttpMethod = Literal["GET", "POST", "PUT", "DELETE", "PATCH"]


class _TopomojoBase:
    """Shared state for the Topomojo client and its endpoint mixins."""

    def __init__(self, app_url: Optional[str] = None, api_key: Optional[str] = None, debug: bool = False) -> None:
        """Create a new :class:`Topomojo` client.

        Parameters
        ----------
        app_url: str, optional
            Base URL to the TopoMojo application (e.g. ``https://example.com/topomojo``).
            Falls back to the ``TOPOMOJO_URL`` environment variable if not provided.
        api_key: str, optional
            API key used for authentication.
            Falls back to the ``TOPOMOJO_API_KEY`` environment variable if not provided.
        debug: bool, optional
            When ``True`` debug logging is enabled.
        """

        resolved_url = app_url if app_url is not None else os.environ.get("TOPOMOJO_URL")
        resolved_key = api_key if api_key is not None else os.environ.get("TOPOMOJO_API_KEY")
        if not resolved_url:
            raise ValueError("app_url is required or set TOPOMOJO_URL environment variable")
        if not resolved_key:
            raise ValueError("api_key is required or set TOPOMOJO_API_KEY environment variable")
        self.app_url = resolved_url
        self.api_key = resolved_key
        self.session = requests.Session()
        self.session.headers.update(
            {'accept': 'application/json', 'x-api-key': self.api_key})

        self.logger = logging.getLogger(__name__)

        if debug:
            self.logger.setLevel(logging.DEBUG)
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)
            self.logger.debug("Topomojo class initialized with logging enabled")
        else:
            self.logger.disabled = True

    def _request_raw(self, method: HttpMethod, path: str, **kwargs: Any) -> requests.Response:
        """Send a request and return the raw Response; raise on non-200."""

        self.logger.debug(
            f"{method} {path} params={kwargs.get('params')} json={kwargs.get('json')}"
        )
        response = self.session.request(method, f"{self.app_url}{path}", **kwargs)
        if response.status_code != 200:
            raise TopomojoException(response.status_code, response.text)
        return response

    def _request(self, method: HttpMethod, path: str, **kwargs: Any) -> Optional[Any]:
        """Send a request; raise on non-200, return decoded JSON or None."""

        return self._json_or_none(self._request_raw(method, path, **kwargs))

    def _json_or_none(self, response: requests.Response) -> Optional[Any]:
        """Return JSON payload or None when the response body is empty."""

        if not response.content:
            return None
        try:
            return response.json()
        except ValueError as exc:
            raise TopomojoException(
                response.status_code, response.text) from exc

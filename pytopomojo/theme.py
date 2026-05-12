from typing import Any, Optional

from ._base import _TopomojoBase


class ThemeMixin(_TopomojoBase):
    """Mixin providing Theme API endpoints."""

    def get_theme(self) -> Optional[Any]:
        """Get the current application theme info."""

        return self._request("GET", "/api/theme")

    def get_theme_background(self) -> Optional[Any]:
        """Get the current application theme background image."""

        return self._request("GET", "/api/theme/background")

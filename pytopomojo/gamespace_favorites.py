"""Gamespace favorites API endpoints."""

from typing import Any, Optional

from ._base import _TopomojoBase


class GamespaceFavoritesMixin(_TopomojoBase):
    """Mixin providing Gamespace Favorites API endpoints."""

    def list_gamespace_favorites(self) -> Optional[Any]:
        """List the current user's favorited gamespace IDs."""

        return self._request("GET", "/api/gamespace-favorites")

    def favorite_gamespace(self, gamespace_id: str) -> Optional[Any]:
        """Add a gamespace to the current user's favorites."""

        return self._request("PUT", f"/api/gamespace-favorite/{gamespace_id}")

    def unfavorite_gamespace(self, gamespace_id: str) -> Optional[Any]:
        """Remove a gamespace from the current user's favorites."""

        return self._request("DELETE", f"/api/gamespace-favorite/{gamespace_id}")

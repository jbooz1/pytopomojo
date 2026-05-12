from typing import Any, Optional

from ._base import _TopomojoBase


class WorkspaceFavoritesMixin(_TopomojoBase):
    """Mixin providing Workspace Favorites API endpoints."""

    def list_workspace_favorites(self) -> Optional[Any]:
        """List the current user's favorited workspace IDs."""

        return self._request("GET", "/api/workspace-favorites")

    def favorite_workspace(self, workspace_id: str) -> Optional[Any]:
        """Add a workspace to the current user's favorites."""

        return self._request("PUT", f"/api/workspace-favorite/{workspace_id}")

    def unfavorite_workspace(self, workspace_id: str) -> Optional[Any]:
        """Remove a workspace from the current user's favorites."""

        return self._request("DELETE", f"/api/workspace-favorite/{workspace_id}")

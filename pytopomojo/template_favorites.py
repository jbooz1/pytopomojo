from typing import Any, Optional

from ._base import _TopomojoBase


class TemplateFavoritesMixin(_TopomojoBase):
    """Mixin providing Template Favorites API endpoints."""

    def list_template_favorites(self) -> Optional[Any]:
        """List the current user's favorited template IDs."""

        return self._request("GET", "/api/template-favorites")

    def favorite_template(self, template_id: str) -> Optional[Any]:
        """Add a template to the current user's favorites."""

        return self._request("PUT", f"/api/template-favorite/{template_id}")

    def unfavorite_template(self, template_id: str) -> Optional[Any]:
        """Remove a template from the current user's favorites."""

        return self._request("DELETE", f"/api/template-favorite/{template_id}")

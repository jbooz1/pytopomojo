from typing import Any, Dict, List, Optional

from ._base import _TopomojoBase


class UserMixin(_TopomojoBase):
    """Mixin providing User API endpoints."""

    def list_users(self, isServiceAccount: Optional[bool] = None, scope: Optional[str] = None,
                   Term: Optional[str] = None, Skip: Optional[int] = None, Take: Optional[int] = None,
                   Sort: Optional[str] = None, Filter: Optional[List[str]] = None) -> Optional[Any]:
        """List users. (admin only)"""

        params = {
            "isServiceAccount": isServiceAccount,
            "scope": scope,
            "Term": Term,
            "Skip": Skip,
            "Take": Take,
            "Sort": Sort,
            "Filter": Filter,
        }
        return self._request("GET", "/api/users", params=params)

    def list_user_scopes(self) -> Optional[Any]:
        """List all available user scopes."""

        return self._request("GET", "/api/user/scopes")

    def get_user(self, user_id: str) -> Optional[Any]:
        """Get a user profile by ID or 'me'."""

        return self._request("GET", f"/api/user/{user_id}")

    def get_user_workspaces(self, user_id: str) -> Optional[Any]:
        """Get workspaces belonging to a user."""

        return self._request("GET", f"/api/user/{user_id}/workspaces")

    def get_user_gamespaces(self, user_id: str) -> Optional[Any]:
        """Get gamespaces belonging to a user."""

        return self._request("GET", f"/api/user/{user_id}/gamespaces")

    def add_or_update_user(self, changed_user: Dict[str, Any]) -> Optional[Any]:
        """Create or update a user profile."""

        return self._request("POST", "/api/user", json=changed_user)

    def delete_user(self, user_id: str) -> Optional[Any]:
        """Delete a user by ID."""

        return self._request("DELETE", f"/api/user/{user_id}")

    def is_user_worker(self, user_id: str) -> Optional[Any]:
        """Check whether a user is a worker."""

        return self._request("GET", f"/api/user/{user_id}/worker")

    def get_user_keys(self, user_id: str) -> Optional[Any]:
        """Get API key records for a user (no key values returned)."""

        return self._request("GET", f"/api/user/{user_id}/keys")

    def create_user_key(self, user_id: str) -> Optional[Any]:
        """Generate a new API key for a user."""

        return self._request("POST", f"/api/apikey/{user_id}")

    def delete_user_key(self, key_id: str) -> Optional[Any]:
        """Delete an API key by key ID."""

        return self._request("DELETE", f"/api/apikey/{key_id}")

    def get_one_time_ticket(self) -> Optional[Any]:
        """Get a one-time authentication ticket for WebSocket connections."""

        return self._request("GET", "/api/user/ticket")

    def get_app_version(self) -> Optional[Any]:
        """Get application version information."""

        return self._request("GET", "/api/version")

from typing import Any, Dict, List, Optional

from ._base import _TopomojoBase


class GamespaceMixin(_TopomojoBase):
    """Mixin providing Gamespace API endpoints."""

    def get_gamespaces(self, WantsAll: Optional[bool] = None, WantsActive: Optional[bool] = None,
                       Term: Optional[str] = None, Skip: Optional[int] = None, Take: Optional[int] = None,
                       Sort: Optional[str] = None, Filter: Optional[List[str]] = None) -> Optional[Any]:
        """List gamespaces available to the user.

        Parameters correspond to the query arguments documented by the
        TopoMojo API and are passed directly to the endpoint.
        """

        params = {
            "WantsAll": WantsAll,
            "WantsActive": WantsActive,
            "Term": Term,
            "Skip": Skip,
            "Take": Take,
            "Sort": Sort,
            "Filter": Filter,
        }
        return self._request("GET", "/api/gamespaces", params=params)

    def preview_gamespace(self, workspace_id: str) -> Optional[Any]:
        """Preview a gamespace from a workspace without registering it."""

        return self._request("GET", f"/api/preview/{workspace_id}")

    def get_gamespace(self, gamespace_id: str) -> Optional[Any]:
        """Load a gamespace state by gamespace or workspace ID."""

        return self._request("GET", f"/api/gamespace/{gamespace_id}")

    def get_gamespace_challenge_progress(self, gamespace_id: str) -> Optional[Any]:
        """Load challenge progress for a gamespace."""

        return self._request("GET", f"/api/gamespace/{gamespace_id}/challenge/progress")

    def register_gamespace(self, registration: Dict[str, Any]) -> Optional[Any]:
        """Register a gamespace on behalf of a user."""

        return self._request("POST", "/api/gamespace", json=registration)

    def update_gamespace(self, changed_gamespace: Dict[str, Any]) -> Optional[Any]:
        """Update a gamespace."""

        return self._request("PUT", "/api/gamespace", json=changed_gamespace)

    def start_gamespace(self, gamespace_id: str) -> Optional[Any]:
        """Start a gamespace."""

        return self._request("POST", f"/api/gamespace/{gamespace_id}/start")

    def stop_gamespace(self, gamespace_id: str) -> Optional[Any]:
        """Stop a running gamespace."""

        return self._request("POST", f"/api/gamespace/{gamespace_id}/stop")

    def complete_gamespace(self, gamespace_id: str) -> Optional[Any]:
        """Mark a gamespace as complete."""

        return self._request("POST", f"/api/gamespace/{gamespace_id}/complete")

    def grade_challenge(self, submission: Dict[str, Any]) -> Optional[Any]:
        """Grade a challenge by submitting answers."""

        return self._request("POST", "/api/gamespace/grade", json=submission)

    def regrade_challenge(self, gamespace_id: str) -> Optional[Any]:
        """Regrade a challenge for a gamespace."""

        return self._request("POST", f"/api/gamespace/{gamespace_id}/regrade")

    def audit_challenge(self, gamespace_id: str) -> Optional[Any]:
        """Audit all submissions for a gamespace challenge."""

        return self._request("POST", f"/api/gamespace/{gamespace_id}/audit")

    def delete_gamespace(self, gamespace_id: str) -> Optional[Any]:
        """Delete a gamespace."""

        return self._request("DELETE", f"/api/gamespace/{gamespace_id}")

    def get_gamespace_invitation(self, gamespace_id: str) -> Optional[Any]:
        """Get an invitation code for a gamespace."""

        return self._request("POST", f"/api/gamespace/{gamespace_id}/invite")

    def remove_gamespace_player(self, gamespace_id: str, subject_id: str) -> Optional[Any]:
        """Remove a player from a gamespace."""

        return self._request("DELETE", f"/api/gamespace/{gamespace_id}/player/{subject_id}")

    def get_gamespace_players(self, gamespace_id: str) -> Optional[Any]:
        """List all players in a gamespace."""

        return self._request("GET", f"/api/players/{gamespace_id}")

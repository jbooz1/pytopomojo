from typing import Any, Dict, List, Optional

from ._base import _TopomojoBase


class DispatchMixin(_TopomojoBase):
    """Mixin providing Dispatch API endpoints."""

    def list_dispatches(self, gs: Optional[str] = None, since: Optional[str] = None,
                        Term: Optional[str] = None, Skip: Optional[int] = None,
                        Take: Optional[int] = None, Sort: Optional[str] = None,
                        Filter: Optional[List[str]] = None) -> Optional[Any]:
        """Find dispatches."""

        params = {
            "gs": gs,
            "since": since,
            "Term": Term,
            "Skip": Skip,
            "Take": Take,
            "Sort": Sort,
            "Filter": Filter,
        }
        return self._request("GET", "/api/dispatches", params=params)

    def create_dispatch(self, new_dispatch: Dict[str, Any]) -> Optional[Any]:
        """Create a new dispatch."""

        return self._request("POST", "/api/dispatch", json=new_dispatch)

    def update_dispatch(self, changed_dispatch: Dict[str, Any]) -> Optional[Any]:
        """Update an existing dispatch."""

        return self._request("PUT", "/api/dispatch", json=changed_dispatch)

    def get_dispatch(self, dispatch_id: str) -> Optional[Any]:
        """Retrieve a dispatch by ID."""

        return self._request("GET", f"/api/dispatch/{dispatch_id}")

    def delete_dispatch(self, dispatch_id: str) -> Optional[Any]:
        """Delete a dispatch by ID."""

        return self._request("DELETE", f"/api/dispatch/{dispatch_id}")

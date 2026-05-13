"""Admin API endpoints (announcements, import/export, janitor, theme assets)."""

from typing import Any, Dict, List, Optional

from ._base import _TopomojoBase


class AdminMixin(_TopomojoBase):
    """Mixin providing Admin API endpoints."""

    def post_announcement(self, message: str) -> Optional[Any]:
        """Post an announcement to all online users."""

        return self._request("POST", "/api/admin/announce", json=message)

    def export_workspaces(self, ids: List[str]) -> Optional[Any]:
        """Export multiple workspaces by their IDs."""

        return self._request("POST", "/api/admin/export", json=ids)

    def export_workspace(self, workspace_id: str) -> Optional[Any]:
        """Export a single workspace by ID."""

        return self.export_workspaces([workspace_id])

    def import_workspaces(self) -> Optional[Any]:
        """Initiate the workspace import process."""

        return self._request("GET", "/api/admin/import")

    def download_workspaces(self, workspace_ids: List[str], output_file: str) -> bool:
        """Download an export package containing one or more workspaces.
        All workspaces listed will be included in the same export package.

        Returns True on success.
        """

        response = self._request_raw("POST", "/api/admin/download", json=workspace_ids, stream=True)
        with open(output_file, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        return True

    def download_workspace(self, workspace_id: str, output_file: str) -> bool:
        """Download a single workspace export package.

        Returns True on success.
        """

        return self.download_workspaces([workspace_id], output_file)

    def upload_workspace(self, archive_path: str) -> Optional[List[str]]:
        """Upload a single workspace export package."""

        with open(archive_path, "rb") as archive:
            return self._request("POST", "/api/admin/upload", files={"files": archive})

    def upload_workspaces(self, archive_paths: List[str]) -> List[str]:
        """Upload multiple workspace export packages."""

        uploaded_ids: List[str] = []
        for path in archive_paths:
            uploaded = self.upload_workspace(path)
            if uploaded:
                uploaded_ids.extend(uploaded)
        return uploaded_ids

    def list_active_users(self) -> Optional[Any]:
        """List currently online users."""

        return self._request("GET", "/api/admin/live")

    def run_janitor(self, options: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """Run janitor cleanup tasks."""

        return self._request("POST", "/api/admin/janitor", json=options)

    def run_janitor_idle_workspace_vms(self, options: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """Run janitor cleanup for idle workspace VMs."""

        return self._request("POST", "/api/admin/janitor/idlewsvms", json=options)

    def get_admin_log(self, since: Optional[str] = None) -> Optional[Any]:
        """Retrieve the admin exception log."""

        return self._request("GET", "/api/admin/log", params={"since": since})

    def upload_background(self, file_path: str) -> Optional[Any]:
        """Upload a background image for the application theme."""

        with open(file_path, "rb") as f:
            return self._request("POST", "/api/admin/background", files={"File": f})

    def delete_background(self) -> Optional[Any]:
        """Delete the current application background image."""

        return self._request("DELETE", "/api/admin/background")

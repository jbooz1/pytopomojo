import os
import re
import uuid
import tempfile
from io import BytesIO
from time import sleep
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import pycdlib
import requests

from ._base import _TopomojoBase
from .exceptions import TopomojoException


class WorkspaceMixin(_TopomojoBase):
    """Mixin providing Workspace and file upload API endpoints."""

    def get_workspaces(self, aud: Optional[str] = None, scope: Optional[str] = None, doc: Optional[int] = None,
                       WantsAudience: Optional[bool] = None, WantsManaged: Optional[bool] = None,
                       WantsDoc: Optional[bool] = None, WantsPartialDoc: Optional[bool] = None,
                       Term: Optional[str] = None, Skip: Optional[int] = None, Take: Optional[int] = None,
                       Sort: Optional[str] = None, Filter: Optional[List[str]] = None) -> Optional[List[Dict[str, Any]]]:
        """List workspaces matching the provided criteria.

        Parameters correspond to the query arguments documented by the
        TopoMojo API and are passed directly to the endpoint.
        """

        params = {
            "aud": aud,
            "scope": scope,
            "doc": doc,
            "WantsAudience": WantsAudience,
            "WantsManaged": WantsManaged,
            "WantsDoc": WantsDoc,
            "WantsPartialDoc": WantsPartialDoc,
            "Term": Term,
            "Skip": Skip,
            "Take": Take,
            "Sort": Sort,
            "Filter": Filter,
        }
        return self._request("GET", "/api/workspaces", params=params)

    def get_workspace(self, workspace_id: str) -> Optional[Any]:
        """Load a workspace by ID."""

        return self._request("GET", f"/api/workspace/{workspace_id}")

    def create_workspace(self, new_workspace_data: Dict[str, Any]) -> Optional[Any]:
        """Create a new workspace."""

        return self._request("POST", "/api/workspace", json=new_workspace_data)

    def update_workspace(self, workspace_id: str, changed_workspace_data: Dict[str, Any]) -> Optional[Any]:
        """Modify an existing workspace.

        Server behavior: the `PUT /api/workspace` endpoint expects a full
        `RestrictedChangedWorkspace` payload and requires `name` to be present.
        To allow callers to pass only changed fields, this function:
        - Loads the current workspace via `GET /api/workspace/{id}`.
        - Merges unspecified fields from the current workspace into the payload.
        - Sends a `PUT` to `/api/workspace` with `id` plus merged fields.

        Allowed fields merged/sent: `name`, `description`, `tags`, `author`, `audience`.
        To clear a field, provide it explicitly (e.g., empty string) if allowed by the API.
        """

        changes = changed_workspace_data or {}
        payload: Dict[str, Any] = {'id': workspace_id}
        allowed_fields = ["name", "description", "tags", "author", "audience"]

        current: Dict[str, Any] = {}
        try:
            current = self._request("GET", f"/api/workspace/{workspace_id}") or {}
        except TopomojoException as e:
            self.logger.debug(
                f"Could not load current workspace {workspace_id} (status {e.status_code}); "
                f"will require 'name' in changes."
            )
        except requests.RequestException as e:
            self.logger.debug(f"Error loading current workspace {workspace_id}: {e}")

        for field in allowed_fields:
            if field in changes:
                payload[field] = changes[field]
            elif current and field in current:
                payload[field] = current[field]

        name = payload.get('name')
        if not name or (isinstance(name, str) and not name.strip()):
            if 'name' not in changes and not current:
                raise ValueError(
                    "Workspace name is required for update and could not be loaded from server.")

        return self._request("PUT", "/api/workspace", json=payload)

    def clone_workspace(self, workspace_id: str) -> Optional[Any]:
        """Clone a workspace by ID."""

        return self._request("POST", f"/api/workspace/{workspace_id}/clone")

    def privileged_update_workspace(self, changed_workspace: Dict[str, Any]) -> Optional[Any]:
        """Update a workspace with elevated (admin) privileges."""

        return self._request("PUT", "/api/workspace/priv", json=changed_workspace)

    def delete_workspace(self, workspace_id: str) -> Optional[Any]:
        """Delete a workspace."""

        return self._request("DELETE", f"/api/workspace/{workspace_id}")

    def get_workspace_invite(self, workspace_id: str) -> Optional[Any]:
        """Generate an invite code for a workspace."""

        return self._request("PUT", f"/api/workspace/{workspace_id}/invite")

    def get_workspace_isos(self, workspace_id: str) -> Optional[Any]:
        """Find ISO files available to a workspace."""

        return self._request("GET", f"/api/workspace/{workspace_id}/isos")

    def get_workspace_nets(self, workspace_id: str) -> Optional[Any]:
        """Find virtual networks available to a workspace."""

        return self._request("GET", f"/api/workspace/{workspace_id}/nets")

    def get_workspace_stats(self, workspace_id: str) -> Optional[Any]:
        """Load gamespace statistics generated from a workspace."""

        return self._request("GET", f"/api/workspace/{workspace_id}/stats")

    def get_workspace_templates(self, workspace_id: str) -> Optional[Any]:
        """Load templates available to a workspace."""

        return self._request("GET", f"/api/workspace/{workspace_id}/templates")

    def delete_workspace_games(self, workspace_id: str) -> Optional[Any]:
        """Delete all gamespaces generated from a workspace."""

        return self._request("DELETE", f"/api/workspace/{workspace_id}/games")

    def get_challenge_spec(self, workspace_id: str) -> Optional[Any]:
        """Get the challenge spec for a workspace."""

        return self._request("GET", f"/api/challenge/{workspace_id}")

    def update_challenge_spec(self, workspace_id: str, spec: Dict[str, Any]) -> Optional[Any]:
        """Update the challenge spec for a workspace."""

        return self._request("PUT", f"/api/challenge/{workspace_id}", json=spec)

    def remove_workspace_worker(self, workspace_id: str, subject_id: str) -> Optional[Any]:
        """Remove a worker from a workspace."""

        return self._request("DELETE", f"/api/workspace/{workspace_id}/worker/{subject_id}")

    def upload_iso(self, iso_path: str, workspace_id: str, is_global: bool = False, wait: bool = False) -> Optional[Any]:
        """Upload a file to a workspace. Non-ISO files are automatically
        wrapped in an ISO 9660 container by the server after upload.

        Parameters
        ----------
        iso_path: str
            Path to the file to upload.
        workspace_id: str
            ID of the workspace to upload the file to.
        is_global: bool, optional
            When True, upload to the global/public bin instead of
            the workspace bin. Defaults to False.
        wait: bool, optional
            When True, poll until the server has finished processing the
            uploaded file before returning. Defaults to False.
        """

        size = os.path.getsize(iso_path)
        monitor_key = str(uuid.uuid4()) if wait else None

        params: Dict[str, Any] = {"size": size}
        if not is_global:
            params["group-key"] = workspace_id
        if monitor_key:
            params["monitor-key"] = monitor_key

        # The server's multipart handler reads all form values from a single section body
        # (parsed as URL-encoded). Sending params as separate sections (requests default)
        # causes each one to overwrite the previous, so encode them all into one section.
        encoded_params = urlencode(params)

        filename = os.path.basename(iso_path)
        with open(iso_path, "rb") as iso_file:
            result = self._request(
                "POST",
                "/api/file/upload",
                files=[
                    ("data", (None, encoded_params, "text/plain")),
                    ("file", (filename, iso_file)),
                ],
            )

        if wait and monitor_key:
            while True:
                try:
                    progress = self._request("GET", f"/api/file/progress/{monitor_key}")
                except TopomojoException:
                    break
                self.logger.debug(f"ISO upload progress: {progress}%")
                if progress is None or progress >= 100 or progress < 0:
                    break
                sleep(1)

        return result

    def upload_directory(self, directory_path: str, workspace_id: str,
                         is_global: bool = False, wait: bool = False,
                         save_iso: Optional[str] = None) -> Optional[Any]:
        """Pack a local directory into an ISO and upload it to a workspace.

        Parameters
        ----------
        directory_path: str
            Path to the directory to pack into an ISO.
        workspace_id: str
            ID of the workspace to upload the ISO to.
        is_global: bool, optional
            When True, upload to the global/public bin instead of the
            workspace bin. Defaults to False.
        wait: bool, optional
            When True, poll until the server has finished processing the
            uploaded file before returning. Defaults to False.
        save_iso: str, optional
            If provided, the generated ISO is written to this path and kept
            after upload. If omitted, the ISO is written to a temporary file
            and deleted after upload.
        """

        if not os.path.isdir(directory_path):
            raise ValueError(f"directory_path must be a directory: {directory_path}")

        if save_iso:
            iso_output_path = save_iso
            cleanup = False
        else:
            fd, iso_output_path = tempfile.mkstemp(suffix='.iso')
            os.close(fd)
            cleanup = True

        self.logger.debug(f"Building ISO from directory {directory_path} -> {iso_output_path}")

        def _iso9660_name(name: str, is_dir: bool) -> str:
            """Sanitize a filename/dirname for ISO 9660 (uppercase, 8.3, A-Z0-9_ only)."""
            name = name.upper()
            name = re.sub(r'[^A-Z0-9_.]', '_', name)
            if is_dir:
                return name[:31]
            base, _, ext = name.rpartition('.')
            if not base:
                base, ext = ext, ''
            return (base[:8] + ('.' + ext[:3] if ext else '')) + ';1'

        open_files: List[BytesIO] = []
        iso = pycdlib.PyCdlib()  # type: ignore[attr-defined]
        iso.new(joliet=3)

        try:
            for root, dirs, files in os.walk(directory_path):
                rel_root = os.path.relpath(root, directory_path)

                if rel_root == '.':
                    iso9660_dir = '/'
                    joliet_dir = '/'
                else:
                    parts = rel_root.replace(os.sep, '/').split('/')
                    iso9660_dir = '/' + '/'.join(_iso9660_name(p, True) for p in parts)
                    joliet_dir = '/' + '/'.join(parts)
                    iso.add_directory(iso9660_dir, joliet_path=joliet_dir)

                for filename in files:
                    file_path = os.path.join(root, filename)
                    with open(file_path, 'rb') as f:
                        data = f.read()
                    fp = BytesIO(data)
                    open_files.append(fp)
                    iso9660_file = iso9660_dir.rstrip('/') + '/' + _iso9660_name(filename, False)
                    joliet_file = joliet_dir.rstrip('/') + '/' + filename
                    iso.add_fp(fp, len(data), iso_path=iso9660_file, joliet_path=joliet_file)

            iso.write(iso_output_path)
        finally:
            iso.close()

        self.logger.debug(f"ISO written to {iso_output_path}, uploading")

        try:
            return self.upload_iso(iso_output_path, workspace_id, is_global=is_global, wait=wait)
        finally:
            if cleanup:
                os.remove(iso_output_path)

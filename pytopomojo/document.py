from typing import Any, Optional

from ._base import _TopomojoBase


class DocumentMixin(_TopomojoBase):
    """Mixin providing Document API endpoints."""

    def load_document(self, workspace_id: str) -> Optional[Any]:
        """Load the markdown document for a workspace."""

        return self._request("GET", f"/api/document/{workspace_id}")

    def save_document(self, workspace_id: str, markdown: str) -> Optional[Any]:
        """Save markdown text as a workspace document."""

        return self._request("PUT", f"/api/document/{workspace_id}", json=markdown)

    def list_document_images(self, workspace_id: str) -> Optional[Any]:
        """List image files attached to a workspace document."""

        return self._request("GET", f"/api/images/{workspace_id}")

    def delete_document_image(self, workspace_id: str, filename: str) -> Optional[Any]:
        """Delete a document image file from a workspace."""

        return self._request("DELETE", f"/api/image/{workspace_id}", params={"filename": filename})

    def upload_document_image(self, workspace_id: str, file_path: str) -> Optional[Any]:
        """Upload an image file to attach to a workspace document."""

        with open(file_path, "rb") as f:
            return self._request("POST", f"/api/image/{workspace_id}", files={"file": f})

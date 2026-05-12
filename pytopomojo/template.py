from time import sleep
from typing import Any, Dict, List, Optional

from ._base import _TopomojoBase


class TemplateMixin(_TopomojoBase):
    """Mixin providing Template API endpoints."""

    def get_templates(self, WantsAudience: Optional[bool] = None, WantsPublished: Optional[bool] = None,
                      WantsParents: Optional[bool] = None, aud: Optional[str] = None,
                      pid: Optional[str] = None, sib: Optional[str] = None,
                      Term: Optional[str] = None, Skip: Optional[int] = None,
                      Take: Optional[int] = None, Sort: Optional[str] = None,
                      Filter: Optional[List[str]] = None) -> Optional[Any]:
        """Get templates from TopoMojo.

        Parameters correspond to the query arguments documented by the
        TopoMojo API and are passed directly to the endpoint.
        """

        params = {
            'WantsAudience': WantsAudience,
            'WantsPublished': WantsPublished,
            'WantsParents': WantsParents,
            'aud': aud,
            'pid': pid,
            'sib': sib,
            'Term': Term,
            'Skip': Skip,
            'Take': Take,
            'Sort': Sort,
            'Filter': Filter,
        }
        return self._request("GET", "/api/templates", params=params)

    def list_template_siblings(self, template_id: str, pub: Optional[bool] = None) -> Optional[Any]:
        """List sibling templates (same parent) for a given template."""

        return self._request("GET", f"/api/template/{template_id}/siblings", params={"pub": pub})

    def load_template(self, template_id: str) -> Optional[Any]:
        """Load a template by ID."""

        return self._request("GET", f"/api/template/{template_id}")

    def delete_template(self, template_id: str) -> Optional[Any]:
        """Delete a template by ID."""

        return self._request("DELETE", f"/api/template/{template_id}")

    def update_template(self, changed_template: Dict[str, Any]) -> Optional[Any]:
        """Update an existing template with new data that is passed directly to the TopoMojo API."""

        return self._request("PUT", "/api/template", json=changed_template)

    def new_workspace_template(self, template_link_data: Dict[str, Any]) -> Optional[Any]:
        """Add a template to a workspace."""

        return self._request("POST", "/api/template", json=template_link_data)

    def unlink_template(self, template_link_data: Dict[str, Any]) -> Optional[Any]:
        """Unlink a template from a parent."""

        return self._request("POST", "/api/template/unlink", json=template_link_data)

    def relink_template(self, relink_data: Dict[str, Any]) -> Optional[Any]:
        """Change a template's parent (relink)."""

        return self._request("POST", "/api/template/relink", json=relink_data)

    def get_template(self, template_id: str) -> Optional[Any]:
        """Get a template by ID."""

        return self._request("GET", f"/api/vm-template/{template_id}")

    def get_template_detail(self, template_id: str) -> Optional[Any]:
        """Get full template details by ID."""

        return self._request("GET", f"/api/template-detail/{template_id}")

    def create_template_detail(self, new_template_detail: Dict[str, Any]) -> Optional[Any]:
        """Create a new template with full detail."""

        return self._request("POST", "/api/template-detail", json=new_template_detail)

    def configure_template_detail(self, changed_template_detail: Dict[str, Any]) -> Optional[Any]:
        """Update template detail configuration."""

        return self._request("PUT", "/api/template-detail", json=changed_template_detail)

    def clone_template(self, clone_data: Dict[str, Any]) -> Optional[Any]:
        """Clone a template."""

        return self._request("POST", "/api/template/clone", json=clone_data)

    def initialize_template(self, template_id: str, wait: bool = True) -> Optional[Any]:
        """Initialize a template after it has been unlinked.
        Optionally wait for completion.
        """

        result = self._request("PUT", f"/api/vm-template/{template_id}")
        if wait:
            while True:
                check = self.get_template(template_id)
                task = check.get('task') if check is not None else None
                if task:
                    self.logger.debug(f"Initializing {task['progress']}%")
                    sleep(1)
                else:
                    self.logger.debug("Done Initializing")
                    break
        return result

    def deploy_vm_from_template(self, template_id: str) -> Optional[Any]:
        """Deploy a VM from an existing template."""

        return self._request("POST", f"/api/vm-template/{template_id}")

    def get_attached_disks_report(self) -> Optional[Any]:
        """Get a report of attached disks across all templates."""

        return self._request("GET", "/api/report/disks")

    def check_template_health(self, template_id: str) -> Optional[Any]:
        """Check health status for a template."""

        return self._request("GET", f"/api/healthz/{template_id}")

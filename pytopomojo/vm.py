"""VM API endpoints (lifecycle, reconfiguration, console access)."""

from typing import Any, Dict, Optional

from ._base import _TopomojoBase


class VmMixin(_TopomojoBase):
    """Mixin providing VM API endpoints."""

    def list_vms(self, filter: Optional[str] = None) -> Optional[Any]:
        """List VMs, optionally filtered by a search string."""

        return self._request("GET", "/api/vms", params={"filter": filter})

    def get_vm(self, vm_id: str) -> Optional[Any]:
        """Load a VM by ID."""

        return self._request("GET", f"/api/vm/{vm_id}")

    def delete_vm(self, vm_id: str) -> Optional[Any]:
        """Delete a VM by ID."""

        return self._request("DELETE", f"/api/vm/{vm_id}")

    def change_vm(self, operation: Dict[str, Any]) -> Optional[Any]:
        """Change VM state (Start, Stop, Save, Revert)."""

        return self._request("PUT", "/api/vm", json=operation)

    def reconfigure_vm(self, vm_id: str, key_value: Dict[str, Any]) -> Optional[Any]:
        """Change a VM's ISO or network attachment."""

        return self._request("PUT", f"/api/vm/{vm_id}/change", json=key_value)

    def answer_vm_question(self, vm_id: str, answer: Dict[str, Any]) -> Optional[Any]:
        """Answer a pending VM question (e.g. VMware question dialog)."""

        return self._request("PUT", f"/api/vm/{vm_id}/answer", json=answer)

    def get_vm_iso_options(self, vm_id: str) -> Optional[Any]:
        """Find ISO files available to a VM."""

        return self._request("GET", f"/api/vm/{vm_id}/isos")

    def get_vm_net_options(self, vm_id: str) -> Optional[Any]:
        """Find virtual networks available to a VM."""

        return self._request("GET", f"/api/vm/{vm_id}/nets")

    def get_vm_console_ticket(self, vm_id: str) -> Optional[Any]:
        """Request a console access ticket for a VM."""

        return self._request("GET", f"/api/vm-console/{vm_id}")

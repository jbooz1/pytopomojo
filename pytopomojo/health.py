"""Health API endpoints."""

from typing import Any, Optional

from ._base import _TopomojoBase


class HealthMixin(_TopomojoBase):
    """Mixin providing Health API endpoints."""

    def get_health_version(self) -> Optional[Any]:
        """Get the application health version string."""

        return self._request("GET", "/api/health/version")

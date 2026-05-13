"""Top-level `Topomojo` client class.

The client is composed of per-area mixins (workspaces, templates,
gamespaces, VMs, users, admin, etc.). All API methods from every mixin
are available on a single `Topomojo` instance.
"""

from ._base import _TopomojoBase
from .admin import AdminMixin
from .dispatch import DispatchMixin
from .document import DocumentMixin
from .exceptions import TopomojoException
from .gamespace import GamespaceMixin
from .gamespace_favorites import GamespaceFavoritesMixin
from .health import HealthMixin
from .template import TemplateMixin
from .template_favorites import TemplateFavoritesMixin
from .theme import ThemeMixin
from .user import UserMixin
from .vm import VmMixin
from .workspace import WorkspaceMixin
from .workspace_favorites import WorkspaceFavoritesMixin

__all__ = ["Topomojo", "TopomojoException"]


class Topomojo(
    AdminMixin,
    DispatchMixin,
    DocumentMixin,
    GamespaceMixin,
    GamespaceFavoritesMixin,
    HealthMixin,
    TemplateMixin,
    TemplateFavoritesMixin,
    ThemeMixin,
    UserMixin,
    VmMixin,
    WorkspaceMixin,
    WorkspaceFavoritesMixin,
    _TopomojoBase,
):
    """Client for interacting with a TopoMojo instance.

    Instantiate with the base URL of a TopoMojo deployment and an API
    key, or set the `TOPOMOJO_URL` and `TOPOMOJO_API_KEY` environment
    variables and construct with no arguments.

    Example:
        ```python
        from pytopomojo import Topomojo

        topomojo = Topomojo("https://example.com/topomojo", "<api-key>")
        topomojo.get_workspaces()
        ```

    Errors returned by the API are raised as
    `pytopomojo.TopomojoException`.
    """

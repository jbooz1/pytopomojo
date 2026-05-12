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
    """Client for interacting with a TopoMojo instance."""

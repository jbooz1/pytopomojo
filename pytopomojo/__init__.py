"""Python client library for the TopoMojo REST API.

`pytopomojo` wraps the TopoMojo HTTP API in a single client class,
`Topomojo`, whose methods mirror the endpoint groups documented by
TopoMojo (workspaces, templates, gamespaces, VMs, users, admin, and
more).

Quick start:

```python
from pytopomojo import Topomojo

topomojo = Topomojo("https://example.com/topomojo", "<api-key>")
workspaces = topomojo.get_workspaces()
```

Alternatively, set the `TOPOMOJO_URL` and `TOPOMOJO_API_KEY` environment
variables and construct the client with no arguments.

Errors returned by the API are raised as `TopomojoException`.
"""

from .exceptions import TopomojoException
from .pytopomojo import Topomojo

__all__ = ["Topomojo", "TopomojoException"]

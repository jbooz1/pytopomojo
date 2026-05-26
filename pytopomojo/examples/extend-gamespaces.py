# This script will extend the expiration of every active gamespace by 4 hours.
# It lists active gamespaces, then for each one PUTs an updated gamespace with
# its expirationTime shifted forward by EXTEND_HOURS.
#
# The TopoMojo URL and API key are read from the TOPOMOJO_URL and
# TOPOMOJO_API_KEY environment variables.

import os
from datetime import datetime, timedelta, timezone

from pytopomojo import Topomojo, TopomojoException

EXTEND_HOURS = 4

topomojo = Topomojo(
    os.environ["TOPOMOJO_URL"],
    os.environ["TOPOMOJO_API_KEY"],
)

gamespaces = topomojo.get_gamespaces(WantsAll=True, WantsActive=True) or []
if not gamespaces:
    raise RuntimeError("No active gamespaces returned")

extended = 0
failures: list[tuple[str, str]] = []

for gs in gamespaces:
    gs_id = gs.get("id")
    name = gs.get("name") or gs_id
    raw_expiration = gs.get("expirationTime")
    if not gs_id or not raw_expiration:
        print(f"SKIP {name}: missing id or expirationTime")
        continue

    # TopoMojo serializes expirationTime as ISO 8601 with a trailing 'Z' for UTC;
    # fromisoformat only accepts '+00:00' on older Python versions.
    current = datetime.fromisoformat(raw_expiration.replace("Z", "+00:00"))
    new_expiration = current + timedelta(hours=EXTEND_HOURS)
    new_expiration_iso = new_expiration.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    try:
        topomojo.update_gamespace({
            "id": gs_id,
            "expirationTime": new_expiration_iso,
        })
        print(f"OK  {name} ({gs_id}) {raw_expiration} -> {new_expiration_iso}")
        extended += 1
    except TopomojoException as exc:
        print(f"ERR {name} ({gs_id}): {exc}")
        failures.append((gs_id, str(exc)))

print(f"\nDone: extended {extended}/{len(gamespaces)}, {len(failures)} failures")
for gs_id, err in failures:
    print(f"  err - {gs_id}: {err}")

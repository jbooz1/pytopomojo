# This script will:
# 1. List the first N users on the TopoMojo instance (admin-only)
# 2. Register a gamespace from a given workspace for each user, with the user
#    set as the gamespace manager (registration does NOT start the gamespace)
# 3. Fire start_gamespace for every registered gamespace concurrently via a
#    thread pool, since the TopoMojo server blocks each start call until VMs
#    are deployed (see cmu-sei/TopoMojo#27)
# 4. Poll each registered gamespace until all VMs are running (or a timeout
#    is hit), printing per-gamespace completion and total elapsed time
#
# Usage: python deploy-gamespaces-for-users.py <workspace_id>
#
# The TopoMojo URL and API key are read from the TOPOMOJO_URL and
# TOPOMOJO_API_KEY environment variables.

import argparse
import os
import time
from concurrent.futures import ThreadPoolExecutor

from requests.adapters import HTTPAdapter

from pytopomojo import Topomojo, TopomojoException

USER_COUNT = 20
POLL_INTERVAL_SECONDS = 10
POLL_TIMEOUT_SECONDS = 30 * 60

parser = argparse.ArgumentParser(description="Register and start a gamespace from a workspace for each user.")
parser.add_argument("workspace_id", help="The workspace ID to register gamespaces from")
args = parser.parse_args()
WORKSPACE_ID = args.workspace_id

topomojo = Topomojo(
    os.environ["TOPOMOJO_URL"],
    os.environ["TOPOMOJO_API_KEY"],
)

# Bump the session's connection pool so every concurrent start_gamespace call
# gets its own connection instead of urllib3 discarding the overflow.
adapter = HTTPAdapter(pool_connections=USER_COUNT, pool_maxsize=USER_COUNT)
topomojo.session.mount("http://", adapter)
topomojo.session.mount("https://", adapter)

raw_users = topomojo.list_users() or []
users = [u for u in raw_users if u.get("role") != "disabled"][:USER_COUNT]
if not users:
    raise RuntimeError("No non-disabled users returned from list_users")

# GET /api/vms?filter=<gamespace_id> returns all hypervisor-instantiated VMs
# for a gamespace (including hidden ones), unlike GameState.vms which hides
# templates marked isHidden. Pull the workspace templates once to compute the
# expected total. Gamespaces are registered without a variant (defaults to 0),
# so match the server filter: Variant == 0 always deploys; other variants
# require an explicit match.
workspace = topomojo.get_workspace(WORKSPACE_ID) or {}
expected_vms = sum(
    max(1, t.get("replicas") or 1)
    for t in (workspace.get("templates") or [])
    if (t.get("variant") or 0) == 0
)

registered: list[tuple[str, str]] = []
failures: list[tuple[str, str]] = []

start_time = time.monotonic()

for user in users:
    user_id = user["id"]
    user_name = user["name"]
    try:
        gamespace = topomojo.register_gamespace({
            "resourceId": WORKSPACE_ID,
            "managerId": user_id,
            "managerName": user_name,
            "startGamespace": False,
            "maxAttempts": 3,
            "maxMinutes": 60,
            "points": 100,
            "allowReset": True,
            "allowPreview": True,
            "players": [{"subjectId": user_id, "subjectName": user_name}],
        })
        if not gamespace or "id" not in gamespace:
            raise TopomojoException(0, "register_gamespace returned no id")
        print(f"REG {user_name} -> gamespace {gamespace['id']}")
        registered.append((user_name, gamespace["id"]))
    except TopomojoException as exc:
        print(f"ERR {user_name}: {exc}")
        failures.append((user_name, str(exc)))

if not registered:
    raise RuntimeError("No gamespaces registered; nothing to start")

executor = ThreadPoolExecutor(max_workers=len(registered))
start_futures = {
    executor.submit(topomojo.start_gamespace, gs_id): (name, gs_id)
    for name, gs_id in registered
}
print(
    f"\nRegistered {len(registered)}/{len(users)}. "
    f"Fired {len(start_futures)} start calls concurrently. "
    f"Polling until all VMs are running..."
)

pending = dict(registered)
timed_out: list[tuple[str, str]] = []

total_expected = expected_vms * len(registered)

while pending and (time.monotonic() - start_time) < POLL_TIMEOUT_SECONDS:
    time.sleep(POLL_INTERVAL_SECONDS)
    print()
    # Gamespaces already removed from pending finished earlier, so their full
    # expected_vms count toward the running total.
    batch_running = expected_vms * (len(registered) - len(pending))
    for name, gs_id in list(pending.items()):
        try:
            vms = topomojo.list_vms(filter=gs_id) or []
        except TopomojoException as exc:
            print(f"ERR poll {name} ({gs_id}): {exc}")
            continue
        created = len(vms)
        running = sum(1 for vm in vms if (vm.get("state") or "").lower() == "running")
        batch_running += running
        elapsed = time.monotonic() - start_time
        if expected_vms and running == expected_vms:
            print(f"UP  {name} ({gs_id}) {running}/{expected_vms} running after {elapsed:.1f}s")
            del pending[name]
        else:
            print(
                f"... {name} ({gs_id}) "
                f"{created}/{expected_vms} created, "
                f"{running}/{expected_vms} running after {elapsed:.1f}s"
            )
    print(
        f"--- {batch_running}/{total_expected} VMs running across all gamespaces "
        f"after {time.monotonic() - start_time:.1f}s"
    )

total_elapsed = time.monotonic() - start_time

if pending:
    for name, gs_id in pending.items():
        print(f"TMO {name} ({gs_id}) still not running after {total_elapsed:.1f}s")
        timed_out.append((name, gs_id))

start_failures: list[tuple[str, str]] = []
for fut, (name, gs_id) in start_futures.items():
    exc = fut.exception()
    if exc is None:
        continue
    # The server blocks each start call until VMs are deployed, so a 504 just
    # means the reverse proxy gave up waiting - the deploy is still proceeding
    # and the poll loop is the source of truth for whether VMs came up.
    if isinstance(exc, TopomojoException) and exc.status_code == 504:
        print(f"504 on start {name} ({gs_id}): ignoring, poll will track it")
        continue
    start_failures.append((name, f"{gs_id}: {exc}"))
executor.shutdown(wait=False)

print(
    f"\nDone: {len(registered) - len(timed_out)} running, "
    f"{len(timed_out)} timed out, {len(failures)} registration failures, "
    f"{len(start_failures)} start failures in {total_elapsed:.1f}s"
)
for name, err in failures:
    print(f"  register err - {name}: {err}")
for name, err in start_failures:
    print(f"  start err - {name} ({err})")
for name, gs_id in timed_out:
    print(f"  timeout - {name} ({gs_id})")

# This script will stop one or more gamespaces. Pass --restart to start each
# gamespace again after they have all been stopped, then poll until every VM
# is running (matching the polling flow from deploy-gamespaces-for-users.py).
#
# Usage: python stop-gamespace.py [--restart] <gamespace_id> [<gamespace_id> ...]
#
# The TopoMojo URL and API key are read from the TOPOMOJO_URL and
# TOPOMOJO_API_KEY environment variables.

import argparse
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

from requests.adapters import HTTPAdapter

from pytopomojo import Topomojo, TopomojoException

POLL_INTERVAL_SECONDS = 10
POLL_TIMEOUT_SECONDS = 30 * 60

parser = argparse.ArgumentParser(description="Stop (and optionally restart) one or more gamespaces.")
parser.add_argument("gamespace_ids", nargs="+", help="One or more gamespace IDs to stop")
parser.add_argument("--restart", action="store_true", help="Start each gamespace again after stopping, then poll until VMs are running")
args = parser.parse_args()

topomojo = Topomojo(
    os.environ["TOPOMOJO_URL"],
    os.environ["TOPOMOJO_API_KEY"],
)

# Stop everything first.
stopped: list[str] = []
stop_failures: list[tuple[str, str]] = []
for gs_id in args.gamespace_ids:
    try:
        topomojo.stop_gamespace(gs_id)
        print(f"STOP  {gs_id}")
        stopped.append(gs_id)
    except TopomojoException as exc:
        print(f"ERR   stop {gs_id}: {exc}", file=sys.stderr)
        stop_failures.append((gs_id, str(exc)))

if not args.restart:
    sys.exit(1 if stop_failures else 0)

if not stopped:
    raise RuntimeError("No gamespaces stopped successfully; nothing to restart")

# Compute the expected VM count for each gamespace by looking up its workspace.
# Variant defaults to 0 on existing gamespaces; match the same server-side
# filter used by the deploy example so the count lines up with what gets
# instantiated.
gs_expected: dict[str, int] = {}
for gs_id in stopped:
    gs = topomojo.get_gamespace(gs_id) or {}
    workspace_id = gs.get("workspaceId")
    if not workspace_id:
        print(f"WARN  no workspaceId for {gs_id}; expected VM count unknown")
        gs_expected[gs_id] = 0
        continue
    workspace = topomojo.get_workspace(workspace_id) or {}
    gs_expected[gs_id] = sum(
        max(1, t.get("replicas") or 1)
        for t in (workspace.get("templates") or [])
        if (t.get("variant") or 0) == 0
    )

# Bump the session's connection pool so every concurrent start_gamespace call
# gets its own connection instead of urllib3 discarding the overflow.
adapter = HTTPAdapter(pool_connections=len(stopped), pool_maxsize=len(stopped))
topomojo.session.mount("http://", adapter)
topomojo.session.mount("https://", adapter)

start_time = time.monotonic()
executor = ThreadPoolExecutor(max_workers=len(stopped))
start_futures = {
    executor.submit(topomojo.start_gamespace, gs_id): gs_id
    for gs_id in stopped
}
print(
    f"\nFired {len(start_futures)} start calls concurrently. "
    f"Polling until all VMs are running..."
)

pending: dict[str, str] = {gs_id: gs_id for gs_id in stopped}
timed_out: list[str] = []
total_expected = sum(gs_expected.values())

while pending and (time.monotonic() - start_time) < POLL_TIMEOUT_SECONDS:
    time.sleep(POLL_INTERVAL_SECONDS)
    print()
    batch_running = sum(gs_expected[g] for g in stopped if g not in pending)
    for gs_id in list(pending):
        try:
            vms = topomojo.list_vms(filter=gs_id) or []
        except TopomojoException as exc:
            print(f"ERR   poll {gs_id}: {exc}")
            continue
        expected = gs_expected.get(gs_id, 0)
        created = len(vms)
        running = sum(1 for vm in vms if (vm.get("state") or "").lower() == "running")
        batch_running += running
        elapsed = time.monotonic() - start_time
        if expected and running == expected:
            print(f"UP    {gs_id} {running}/{expected} running after {elapsed:.1f}s")
            del pending[gs_id]
        else:
            print(
                f"...   {gs_id} "
                f"{created}/{expected} created, "
                f"{running}/{expected} running after {elapsed:.1f}s"
            )
    print(
        f"---   {batch_running}/{total_expected} VMs running across all gamespaces "
        f"after {time.monotonic() - start_time:.1f}s"
    )

total_elapsed = time.monotonic() - start_time

if pending:
    for gs_id in pending:
        print(f"TMO   {gs_id} still not running after {total_elapsed:.1f}s")
        timed_out.append(gs_id)

start_failures: list[tuple[str, str]] = []
for fut, gs_id in start_futures.items():
    exc = fut.exception()
    if exc is None:
        continue
    # The server blocks each start call until VMs are deployed, so a 504 just
    # means the reverse proxy gave up waiting - the deploy is still proceeding
    # and the poll loop is the source of truth for whether VMs came up.
    if isinstance(exc, TopomojoException) and exc.status_code == 504:
        print(f"504   on start {gs_id}: ignoring, poll will track it")
        continue
    start_failures.append((gs_id, str(exc)))
executor.shutdown(wait=False)

print(
    f"\nDone: {len(stopped) - len(timed_out)} running, "
    f"{len(timed_out)} timed out, {len(stop_failures)} stop failures, "
    f"{len(start_failures)} start failures in {total_elapsed:.1f}s"
)
for gs_id, err in stop_failures:
    print(f"  stop err - {gs_id}: {err}")
for gs_id, err in start_failures:
    print(f"  start err - {gs_id}: {err}")
for gs_id in timed_out:
    print(f"  timeout - {gs_id}")

sys.exit(1 if (stop_failures or start_failures or timed_out) else 0)

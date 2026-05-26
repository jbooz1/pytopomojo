# This script will delete VMs in bulk. With no arguments, it deletes every VM
# whose groupName contains "orphaned" and whose name contains "#". If a
# positional argument is given, it deletes every VM whose name contains that
# substring instead - useful for cleaning up by gamespace GUID.
#
# Usage: python delete-vms.py [name_substring]
#
# The TopoMojo URL and API key are read from the TOPOMOJO_URL and
# TOPOMOJO_API_KEY environment variables.

import argparse
import os
import sys
import time

from pytopomojo import Topomojo, TopomojoException

SLEEP_SECONDS = 0.5

ZERO_GUIDS = ("00000000-0000-0000-0000-000000000000", "00000000000000000000000000000000")

parser = argparse.ArgumentParser(description="Delete orphaned VMs, or VMs whose name contains a given substring.")
parser.add_argument(
    "name_substring",
    nargs="?",
    help="If given, delete VMs whose name contains this substring (e.g. a gamespace GUID). Defaults to the orphaned-VM filter.",
)
args = parser.parse_args()

topomojo = Topomojo(
    os.environ["TOPOMOJO_URL"],
    os.environ["TOPOMOJO_API_KEY"],
)

vms = topomojo.list_vms() or []
if args.name_substring:
    needle = args.name_substring
    orphans = [vm for vm in vms if needle in (vm.get("name", ""))]
    label = f"VMs with {needle!r} in name"
else:
    orphans = [
        vm for vm in vms
        if "orphaned" in (vm.get("groupName", ""))
        and "#" in (vm.get("name", ""))
        and not any(z in (vm.get("name", "")) for z in ZERO_GUIDS)
    ]
    label = "orphaned VMs"

if not orphans:
    print(f"No {label} found")
    sys.exit(0)

print(f"Found {len(orphans)} {label}")

deleted = 0
failures: list[tuple[str, str]] = []

for vm in orphans:
    vm_id = vm["id"]
    name = vm.get("name") or vm_id
    try:
        topomojo.delete_vm(vm_id)
        print(f"OK  {name} ({vm_id})")
        deleted += 1
    except TopomojoException as exc:
        print(f"ERR {name} ({vm_id}): {exc}", file=sys.stderr)
        failures.append((vm_id, str(exc)))
    time.sleep(SLEEP_SECONDS)

print(f"\nDone: deleted {deleted}/{len(orphans)}, {len(failures)} failures")
for vm_id, err in failures:
    print(f"  err - {vm_id}: {err}")

sys.exit(1 if failures else 0)

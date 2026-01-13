# This script loads a list of workspace GUIDs and prints the unique template
# disks referenced by those workspaces.
# Usage:
#   python get-disks-from-workspaces.py --workspace-file workspace-guids.txt
# Update the TopoMojo URL and API key below before running.

import argparse
import json
from pathlib import Path
from typing import Iterable, List, Set

from pytopomojo import Topomojo, TopomojoException


def load_workspace_ids(path: Path) -> List[str]:
    """Return non-empty, non-comment lines from the provided file."""

    if not path.exists():
        raise FileNotFoundError(f"Workspace list not found: {path}")

    workspace_ids: List[str] = []
    with path.open("r", encoding="utf-8") as file_handle:
        for line in file_handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            workspace_ids.append(stripped)
    return workspace_ids


def fetch_workspace_template_ids(client: Topomojo, workspace_id: str) -> List[str]:
    """Load the workspace and return the template IDs it references."""

    response = client.session.get(f"{client.app_url}/api/workspace/{workspace_id}")
    if response.status_code != 200:
        raise TopomojoException(response.status_code, response.text)

    workspace = response.json() or {}
    template_entries: Iterable[dict] = (
        workspace.get("templates") or workspace.get("templateLinks") or []
    )

    template_ids: List[str] = []
    for template in template_entries:
        template_id = (
            template.get("templateId")
            or template.get("id")
            or template.get("template", {}).get("id")
        )
        if template_id:
            template_ids.append(template_id)
    return template_ids


def normalize_disk_path(path: str) -> str:
    """Strip datastore prefixes so the same disk matches across templates."""

    prefix = "ds://"
    return path[len(prefix) :] if path.startswith(prefix) else path


def extract_disks_from_detail(template_detail: dict) -> Set[str]:
    """Return disk paths referenced by a template detail payload."""

    detail_payload = template_detail.get("detail")
    if not detail_payload:
        return set()

    try:
        parsed = json.loads(detail_payload)
    except (TypeError, json.JSONDecodeError):
        return set()

    disks: Iterable[dict] = parsed.get("Disks") or []
    disk_paths: Set[str] = set()
    for disk in disks:
        for key in ("Path", "Source"):
            path_value = disk.get(key)
            if path_value:
                disk_paths.add(normalize_disk_path(path_value))
    return disk_paths


def main():
    parser = argparse.ArgumentParser(
        description="Collect unique TopoMojo template disks from workspace IDs."
    )
    parser.add_argument(
        "--workspace-file",
        "-f",
        default="workspace-guids.txt",
        help="Path to a file containing workspace GUIDs (one per line).",
    )
    args = parser.parse_args()

    workspace_file = Path(args.workspace_file)
    workspace_ids = load_workspace_ids(workspace_file)
    if not workspace_ids:
        print(f"No workspace GUIDs found in {workspace_file}")
        return

    topomojo = Topomojo("https://example.com/topomojo", "<put your API Key here>")

    unique_disks: Set[str] = set()
    for workspace_id in workspace_ids:
        print(f"Inspecting workspace {workspace_id}")
        try:
            template_ids = fetch_workspace_template_ids(topomojo, workspace_id)
        except TopomojoException as exc:
            print(f"  Failed to load workspace {workspace_id}: {exc}")
            continue

        if not template_ids:
            print(f"  No templates linked to workspace {workspace_id}")
            continue

        print(f"  Found {len(template_ids)} templates")
        for template_id in template_ids:
            try:
                template_detail = topomojo.get_template_detail(template_id)
            except TopomojoException as exc:
                print(f"    Failed to load template {template_id}: {exc}")
                continue

            disks = extract_disks_from_detail(template_detail)
            if disks:
                print(f"    Collected {len(disks)} disks from template {template_id}")
                unique_disks.update(disks)

    print(f"\nFound {len(unique_disks)} unique disks across {len(workspace_ids)} workspaces.")
    for disk_path in sorted(unique_disks):
        print(disk_path)


if __name__ == "__main__":
    main()

"""Upload workspace archives to TopoMojo based on a list of challenge names."""

import argparse
import os
import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional

from pytopomojo import Topomojo, TopomojoException


def load_challenge_names(path: Path) -> List[str]:
    """Return non-empty, non-comment lines from the provided file."""

    if not path.exists():
        raise FileNotFoundError(f"Workspace list not found: {path}")

    names: List[str] = []
    with path.open("r", encoding="utf-8") as file_handle:
        for line in file_handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            names.append(stripped)
    return names


def slugify(name: str) -> str:
    """Convert a workspace name into a slug to match export filenames."""

    normalized = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    lowered = normalized.lower()
    lowered = lowered.replace("&", " and ")
    slug = re.sub(r"[^a-z0-9]+", "-", lowered)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug


def build_zip_index(workspaces_dir: Path) -> Dict[str, Path]:
    """Map lowercase zip stems to their full paths."""

    if not workspaces_dir.exists():
        raise FileNotFoundError(f"Workspaces directory not found: {workspaces_dir}")

    zip_index: Dict[str, Path] = {}
    for path in workspaces_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() == ".zip":
            zip_index[path.stem.lower()] = path
    return zip_index


def resolve_archive_path(name: str, zip_index: Dict[str, Path]) -> Optional[Path]:
    """Return the archive path for a workspace name if found."""

    slug = slugify(name).lower()
    return zip_index.get(slug)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Upload TopoMojo workspace exports from a list of challenge names."
    )
    parser.add_argument(
        "--workspace-file",
        "-f",
        default="workspaces.txt",
        help="Path to a file containing workspace names (one per line).",
    )
    parser.add_argument(
        "--workspaces-dir",
        "-d",
        default="workspaces",
        help="Directory containing workspace zip exports.",
    )
    parser.add_argument(
        "--app-url",
        default=os.environ.get("TOPOMOJO_URL", "https://example.com/topomojo"),
        help="TopoMojo base URL (or set TOPOMOJO_URL).",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("TOPOMOJO_API_KEY"),
        help="TopoMojo API key (or set TOPOMOJO_API_KEY).",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Upload all archives in one call with upload_workspaces.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print resolved archive paths without uploading.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging for the TopoMojo client.",
    )
    args = parser.parse_args()

    if not args.api_key:
        parser.error("Missing API key. Provide --api-key or set TOPOMOJO_API_KEY.")

    workspace_file = Path(args.workspace_file)
    workspaces_dir = Path(args.workspaces_dir)

    names = load_challenge_names(workspace_file)
    if not names:
        print(f"No workspace names found in {workspace_file}")
        return

    zip_index = build_zip_index(workspaces_dir)
    if not zip_index:
        print(f"No workspace zip files found in {workspaces_dir}")
        return

    archive_paths: List[Path] = []
    missing: List[str] = []

    for name in names:
        path = resolve_archive_path(name, zip_index)
        if path is None:
            missing.append(name)
            continue
        archive_paths.append(path)

    if missing:
        print("Missing workspace archives for:")
        for name in missing:
            print(f"  - {name} (slug: {slugify(name)})")

    if not archive_paths:
        print("No workspace archives resolved for upload.")
        return

    if args.dry_run:
        print("Resolved workspace archives:")
        for path in archive_paths:
            print(f"  - {path}")
        return

    client = Topomojo(args.app_url, args.api_key, debug=args.debug)

    uploaded_ids: List[str] = []
    if args.batch:
        try:
            uploaded_ids = client.upload_workspaces([str(p) for p in archive_paths])
        except TopomojoException as exc:
            print(f"Failed to upload workspace batch: {exc}")
            return
    else:
        for path in archive_paths:
            try:
                uploaded = client.upload_workspace(str(path))
            except TopomojoException as exc:
                print(f"Failed to upload {path}: {exc}")
                continue
            if uploaded:
                uploaded_ids.extend(uploaded)

    print(f"Uploaded {len(uploaded_ids)} workspaces.")
    if uploaded_ids:
        for workspace_id in uploaded_ids:
            print(workspace_id)


if __name__ == "__main__":
    main()

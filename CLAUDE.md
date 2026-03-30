# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

pytopomojo is a Python API client library for [TopoMojo](https://github.com/cmu-sei/TopoMojo), wrapping its REST API. The sole runtime dependency is `requests`. The project is published to PyPI as `pytopomojo`.

## Development Commands

```bash
# Create virtual environment and install in editable mode
make venv

# Remove virtual environment
make clean

# Install from source (editable)
pip install -e .
```

There is no test suite, linter configuration, or formatter configuration in this repository.

## Architecture

The entire library lives in a single module: `pytopomojo/pytopomojo.py`. The package exposes two public names via `pytopomojo/__init__.py`: `Topomojo` (the client class) and `TopomojoException`.

**Topomojo client** — uses a `requests.Session` with an `x-api-key` header for authentication. All API methods follow a consistent pattern: build params/body, make an HTTP call, check for status 200, return JSON or raise `TopomojoException`. The client is organized into three endpoint groups:

- **Workspace methods** — CRUD, export/download/upload (supports streaming and multipart)
- **Template methods** — CRUD, link/unlink to workspaces, initialize (with optional polling), deploy VMs
- **Gamespace methods** — list, stop, complete

Key design choices:
- Query parameters and JSON bodies are passed through directly to the TopoMojo API (kwargs become query params or body fields).
- `update_workspace()` merges caller-provided fields with existing workspace data before PUTting.
- `initialize_template()` accepts `wait=True` to poll until the async operation completes.
- File downloads use chunked streaming; uploads use multipart form data.

## CI/CD

Publishing is handled by `.github/workflows/publish.yaml`. On a GitHub release, the workflow replaces the placeholder version `0.0.0` in `pyproject.toml` with the git tag, builds the package, and publishes to PyPI.

## Examples

`pytopomojo/examples/` contains usage scripts demonstrating workspace creation, template management, batch uploads, and bulk downloads. These serve as both documentation and integration-level smoke tests.

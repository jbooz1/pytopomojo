# PyTopoMojo

This project is a Python API Client that can be used to interact with [TopoMojo](https://github.com/cmu-sei/TopoMojo). It is a work in progress, so not all TopoMojo API endpoints are implemented yet.

## Installation

```
pip install pytopomojo
```

## Dev Container

This repo includes a VS Code Dev Container for a ready-to-code Linux environment.

### Requirements

- Docker Desktop (or Docker Engine)
- VS Code + Dev Containers extension

### Open in Dev Container

- In VS Code, run: `Dev Containers: Reopen in Container`

### SSH Agent (multiple Git identities supported)

- The devcontainer forwards your host SSH agent using the official `ssh-agent` Feature.
- Your host `~/.ssh/config` is mounted read‑only to preserve host aliases like `github.com-work` or `github.com-personal`.

#### Windows setup

- Ensure the "OpenSSH Authentication Agent" Windows service is running (set Startup Type to Automatic).
- Start a PowerShell (or Git Bash) on the host and add your keys:
  - `ssh-add ~\.ssh\id_ed25519_work`
  - `ssh-add ~\.ssh\id_ed25519_personal`
- Keep your aliases in `%USERPROFILE%\.ssh\config`, for example:

  ```
  Host github.com-work
    HostName github.com
    User git
    IdentityAgent SSH_AUTH_SOCK
    IdentityFile ~/.ssh/id_ed25519_work

  Host github.com-personal
    HostName github.com
    User git
    IdentityAgent SSH_AUTH_SOCK
    IdentityFile ~/.ssh/id_ed25519_personal
  ```

- Reopen the folder in the devcontainer; keys remain on the host and are available via the agent.

#### macOS / Linux setup

- Ensure your SSH agent has your keys loaded: `ssh-add -l` (add with `ssh-add ~/.ssh/id_ed25519` if needed).
- Keep aliases in `~/.ssh/config` as above.

#### Verify inside the container

- `ssh -T git@github.com` (or your alias, e.g., `ssh -T git@github.com-work`).
- `git remote -v` can use alias URLs like `git@github.com-work:org/repo.git`.

Notes

- Private keys never enter the container; only the agent is forwarded.
- The devcontainer ensures `~/.ssh/` exists and mounts your `config` file read‑only.

## Upload Workspace Example

```python
from pytopomojo import Topomojo

topomojo = Topomojo("<topomojo_url>", "<topomojo_api_key>")
topomojo.get_workspaces()

# Upload a workspace archive
topomojo.upload_workspace("/path/to/workspace.zip")

# Upload multiple workspace archives
topomojo.upload_workspaces(["/path/one.zip", "/path/two.zip"])
```

## Workspace Update Example

```python
from pytopomojo import Topomojo

tm = Topomojo("<topomojo_url>", "<api_key>")

# Update workspace name and description
tm.update_workspace(
    workspace_id="<workspace-guid>",
    changed_workspace_data={
        "name": "New Name",
        "description": "New Description"
        # 'id' is optional; the client will include it automatically
    }
)
```

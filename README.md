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

- The dev container reuses your host SSH agent so you can keep separate keys for different GitHub accounts without copying private keys into the container.
- Your host `~/.ssh/config` is mounted read-only to preserve host aliases like `github.com-work` or `github.com-personal`.

#### Why `/ssh-agent/proxy.sock`?

Linking the mounted socket to a stable in-container path follows the guidance from the Dev Containers documentation on [sharing Git credentials](https://code.visualstudio.com/remote/advancedcontainers/sharing-git-credentials#_sharing-ssh-keys-with-your-container) and Docker Desktop's instructions for [using the host SSH agent inside a container](https://docs.docker.com/desktop/networking/#use-host-ssh-agent-in-a-container). Both recommend forwarding the host agent through a mounted socket and pointing `SSH_AUTH_SOCK` at that path, which is exactly what the proxy symlink accomplishes.

#### Prepare the host (all platforms)

1. Start an SSH agent and add every key you need (run `ssh-add -l` to verify).
2. Export `SSH_AUTH_SOCK` in the shell that launches VS Code or runs `devcontainer up`.
   - macOS / Linux: launching an agent (`eval "$(ssh-agent)"`) usually sets the variable automatically.
   - Windows: before starting VS Code, set `set SSH_AUTH_SOCK=/run/host-services/ssh-auth.sock` (PowerShell: `$Env:SSH_AUTH_SOCK="/run/host-services/ssh-auth.sock"`).
3. Keep your host `~/.ssh/config` up to date with the aliases and `IdentityFile` entries for each GitHub account you use.

When the container starts it first attempts to mount the socket referenced by `SSH_AUTH_SOCK`. If that is unavailable (for example on Docker Desktop for Windows), the post-start hook falls back to Docker Desktop's `ssh-auth.sock`, which exposes the same agent to Linux containers.

#### Windows specifics

- Ensure the "OpenSSH Authentication Agent" Windows service is running (Startup Type = Automatic).
- In PowerShell or Git Bash, add each key to the agent:
  - `ssh-add ~\.ssh\id_ed25519_work`
  - `ssh-add ~\.ssh\id_ed25519_personal`
- Store aliases in `%USERPROFILE%\.ssh\config`, for example:

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

- Reopen the folder in the dev container; the keys remain on the host and the agent is reused automatically.

#### macOS / Linux specifics

- Verify your keys are loaded with `ssh-add -l`; add them with `ssh-add ~/.ssh/id_ed25519_work` as needed.
- Keep aliases in `~/.ssh/config` as above.
- The post-start hook links the mounted socket to `/ssh-agent/proxy.sock` and sets `SSH_AUTH_SOCK` accordingly.

#### Verify inside the container

Run the following inside the dev container to confirm everything is wired correctly:

- `ls -l /ssh-agent` — shows `proxy.sock` pointing to the mounted host socket.
- `ssh-add -l` — the same keys you added on the host should be listed.
- `ssh -T git@github.com` or `ssh -T git@github.com-work` — GitHub should report successful authentication.
- `git remote -v` — repositories can use alias URLs like `git@github.com-work:org/repo.git`.

Notes

- Private keys never leave the host; only the forwarded agent socket is exposed inside the container.
- The dev container ensures `~/.ssh/` exists and mounts your `config` file read-only so aliases are always available.

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

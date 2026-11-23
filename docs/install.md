# Installing pp

Three ways, one installer. None needs git or Python: the installer brings
[uv](https://docs.astral.sh/uv/), which brings Python.

| way | Linux / macOS | Windows (cmd or PowerShell) |
|---|---|---|
| one command | `curl -LsSf https://raw.githubusercontent.com/VogtVan/pp/main/install.sh \| sh` | `powershell -ExecutionPolicy ByPass -c "irm https://raw.githubusercontent.com/VogtVan/pp/main/install.ps1 \| iex"` |
| the zip | *Code → Download ZIP*, extract, `sh pp-main/install.sh` | *Code → Download ZIP*, extract, double-click `pp-install.cmd` |
| git | `git clone https://github.com/VogtVan/pp.git` then `sh pp/install.sh` | `git clone https://github.com/VogtVan/pp.git` then `pp\pp-install.cmd` |

The one command downloads pp into `pp/` and builds the house in `house/`, both in the
folder you run it from. The zip and git use the folder you extracted or cloned.

## What the installer does

1. If uv is missing, it installs it with uv's own installer, then makes the current
   window find it.
2. It takes pp from the folder the installer stands in. With the one command, it
   downloads pp into `pp/` instead; a `pp/` that is a git clone is left as it is.
3. It builds the house in `house/`, beside pp. If the house is already there, it only
   brings it up to date with `pp upgrade`: your agents, teams and records stay as they are.
4. It writes `pp-ui` (`pp-ui.cmd` on Windows) beside the house. Run it, or double-click
   it, to open the post. A house with another name gets its own: `pp-ui-<name>`.
5. It opens the post.

## Updating

Run the installer again. It takes or downloads the new pp, and the house only gets
`pp upgrade`.

## Options

| option | Linux / macOS | Windows |
|---|---|---|
| another folder for the house | `--house <folder>` | `-House <folder>` |
| another coding agent (`claude` by default) | `--harness codex` | `-Harness codex` |
| other packages (`agent team ui` by default) | `--packages "<names>"` | `-Packages "<names>"` |
| do not open the post at the end | `--no-launch` | `-NoLaunch` |

With the one command on Linux or macOS, options go after `sh -s --`
(`… | sh -s -- --harness codex`); on Windows, use the zip or git to pass them. The options
choose what a new house gets; a house that is already there keeps its packages and its
coding agent (`./pp add <package>` adds a package).

## Your coding agent

The installer does not install your coding agent's command line (`claude`, `codex`,
`gemini`, or Cursor's `agent`): it tells you when it is missing.

## Another source

To fetch pp's archive or uv's installer from another place, set `PP_ARCHIVE` or
`PP_UV_INSTALLER` to a URL or a file.

## What it writes

uv (through uv's own installer, in your user folder), pp itself, the house, and the
post's launcher beside the house. Nothing else.

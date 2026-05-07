# Codex Sound Hooks

Small sound notifications for the OpenAI Codex extension and Codex CLI hook system.

## What It Does

This hook pack keeps Codex quiet until something needs attention:

- `PermissionRequest` plays a short alert sound when Codex asks for approval.
- `Stop` plays a bright completion ding when Codex finishes.

Prompt submit, session start, pre-tool, and post-tool sounds are intentionally left out.

## Install

Copy the `.codex` folder into a project that uses Codex hooks.

Enable hooks globally in `~/.codex/config.toml`:

```toml
[features]
codex_hooks = true
```

The project must be trusted for project-local `.codex` hooks to load.

## Test

```bash
printf '%s\n' '{"reason":"manual test"}' \
  | python3 .codex/hooks/scripts/hooks.py --hook PermissionRequest

printf '%s\n' '{"status":"done"}' \
  | python3 .codex/hooks/scripts/hooks.py --hook Stop
```

## Customize Sounds

Replace these files with your own WAV sounds:

```text
.codex/hooks/sounds/PermissionRequest/PermissionRequest.wav
.codex/hooks/sounds/Stop/Stop.wav
```

Keep the same folder and file names unless you also update `.codex/hooks/scripts/hooks.py`.

## Notes

The hook commands resolve the project root with `git rev-parse --show-toplevel` and fall back to the current working directory.

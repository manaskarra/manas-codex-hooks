#!/usr/bin/env python3
"""Play small notification sounds for selected Codex hook events."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    import winsound
except ImportError:
    winsound = None


HOOK_SOUND_MAP = {
    "PermissionRequest": "PermissionRequest",
    "Stop": "Stop",
}

HOOK_CONFIG_MAP = {
    "PermissionRequest": "disablePermissionRequestHook",
    "Stop": "disableStopHook",
}


def hooks_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def load_config() -> dict[str, object]:
    config_dir = hooks_dir() / "config"
    config = {}

    for path in (
        config_dir / "hooks-config.json",
        config_dir / "hooks-config.local.json",
    ):
        if not path.exists():
            continue

        try:
            config.update(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            pass

    return config


def audio_player() -> list[str] | None:
    system = platform.system()

    if system == "Darwin":
        return ["afplay"]

    if system == "Linux":
        for player in (
            ["paplay"],
            ["aplay"],
            ["ffplay", "-nodisp", "-autoexit"],
        ):
            if subprocess.run(
                ["which", player[0]],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            ).returncode == 0:
                return player

    if system == "Windows" and winsound:
        return ["WINDOWS"]

    return None


def play_sound(sound_name: str) -> None:
    if "/" in sound_name or "\\" in sound_name or ".." in sound_name:
        return

    player = audio_player()
    if not player:
        return

    sound_path = hooks_dir() / "sounds" / sound_name / f"{sound_name}.wav"
    if not sound_path.exists():
        return

    try:
        if player[0] == "WINDOWS":
            winsound.PlaySound(str(sound_path), winsound.SND_FILENAME | winsound.SND_NODEFAULT)
            return

        subprocess.Popen(
            [*player, str(sound_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError:
        pass


def read_payload(event_name: str) -> dict[str, object]:
    payload = {"type": event_name}

    try:
        if not sys.stdin.isatty():
            stdin_data = sys.stdin.read()
            if stdin_data.strip():
                payload.update(json.loads(stdin_data))
    except (OSError, json.JSONDecodeError):
        pass

    payload["type"] = event_name
    return payload


def log_hook(payload: dict[str, object], config: dict[str, object]) -> None:
    if config.get("disableLogging", True):
        return

    logs_dir = hooks_dir() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    entry = {
        "hook": payload.get("type", ""),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }

    with (logs_dir / "hooks-log.jsonl").open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Codex hook sound player")
    parser.add_argument("--hook", required=True, choices=sorted(HOOK_SOUND_MAP))
    args = parser.parse_args()

    config = load_config()
    payload = read_payload(args.hook)
    log_hook(payload, config)

    if config.get(HOOK_CONFIG_MAP[args.hook], False):
        return 0

    play_sound(HOOK_SOUND_MAP[args.hook])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

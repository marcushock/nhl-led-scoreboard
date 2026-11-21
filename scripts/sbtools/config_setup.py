#!/usr/bin/env python3
"""
Create or update config/config.json without the nhl_setup binary.

Use this on Pi Zero / Pi 1 (armv6), or anywhere you prefer a small terminal wizard
over the full nhl_setup UI.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config" / "config.json"
SAMPLE_PATH = REPO_ROOT / "config" / "config.json.sample"
SCHEMA_PATH = REPO_ROOT / "config" / "config.schema.json"

sys.path.insert(0, str(REPO_ROOT / "src"))
from data.validate_json import validateConf  # noqa: E402


def _whiptail(args):
    if not sys.stdin.isatty():
        return None
    try:
        return subprocess.run(
            ["whiptail", "--backtitle", "NHL LED Scoreboard", *args],
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        return None


def _inputbox(title, prompt, default=""):
    result = _whiptail(["--inputbox", prompt, "12", "72", default])
    if result is not None:
        if result.returncode != 0:
            print("Cancelled.")
            sys.exit(1)
        return result.stdout.strip()
    value = input(f"{title} [{default}]: ").strip()
    return value or default


def _yesno(prompt, default_yes=True):
    args = ["--yesno", prompt, "10", "72"]
    if not default_yes:
        args.append("--defaultno")
    result = _whiptail(args)
    if result is not None:
        return result.returncode == 0
    default_hint = "Y/n" if default_yes else "y/N"
    answer = input(f"{prompt} ({default_hint}): ").strip().lower()
    if not answer:
        return default_yes
    return answer in ("y", "yes")


def _load_template():
    if CONFIG_PATH.is_file():
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    if SAMPLE_PATH.is_file():
        with open(SAMPLE_PATH, encoding="utf-8") as f:
            return json.load(f)
    print(f"Missing {SAMPLE_PATH}", file=sys.stderr)
    sys.exit(1)


def _teams_list(teams_csv):
    return [name.strip() for name in teams_csv.split(",") if name.strip()]


def main():
    os.chdir(REPO_ROOT)

    if not CONFIG_PATH.is_file() and SAMPLE_PATH.is_file():
        shutil.copy(SAMPLE_PATH, CONFIG_PATH)
        print(f"Created {CONFIG_PATH} from the sample.")

    config = _load_template()
    prefs = config.setdefault("preferences", {})

    existing_teams = ", ".join(prefs.get("teams") or [])
    teams_csv = _inputbox(
        "Preferred teams",
        "Enter NHL team names, comma-separated\n(example: Maple Leafs, Bruins)",
        existing_teams or "Maple Leafs",
    )
    prefs["teams"] = _teams_list(teams_csv)

    location = _inputbox(
        "Location",
        "City and region for clock, weather, and dimmer\n(example: Toronto, ON)",
        prefs.get("location") or "",
    )
    prefs["location"] = location

    config["live_mode"] = _yesno("Show live games when your teams play?", prefs.get("live_mode", True))

    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent="\t")
        f.write("\n")

    valid, msg = validateConf(str(CONFIG_PATH), str(SCHEMA_PATH))
    if valid:
        print(f"Wrote {CONFIG_PATH} — validation passed.")
        return 0

    print(f"Wrote {CONFIG_PATH}, but validation failed: {msg}", file=sys.stderr)
    print("Fix the file by hand or run this wizard again.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
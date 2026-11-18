#!/usr/bin/env python3
"""Merge one or more QA Forge MCP profiles into a project's .mcp.json (Claude Code format).

Keeps existing servers, never writes secret values (profiles reference ${VAR}), strips _notes.
Example: python scripts/add_mcp_profile.py playwright jira-cloud-oauth ado-azcli --target .mcp.json
"""
import argparse
import json
import sys
from pathlib import Path

PROFILES = Path(__file__).resolve().parent.parent / "mcp-profiles"


def available():
    return sorted(p.stem for p in PROFILES.glob("*.json"))


def merge(target: Path, names, overwrite=False):
    cfg = json.loads(target.read_text()) if target.exists() else {}
    servers = cfg.setdefault("mcpServers", {})
    added, skipped, notes = [], [], []
    for name in names:
        path = PROFILES / f"{name}.json"
        if not path.exists():
            raise SystemExit(f"unknown profile '{name}'. Available: {', '.join(available())}")
        prof = json.loads(path.read_text())
        if prof.get("_notes"):
            notes.append(f"{name}: {prof['_notes']}")
        for key, spec in prof["mcpServers"].items():
            if key in servers and not overwrite:
                skipped.append(key)
                continue
            servers[key] = spec
            added.append(key)
    target.write_text(json.dumps(cfg, indent=2) + "\n")
    return added, skipped, notes


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("profiles", nargs="*", help="profile names (see --list)")
    p.add_argument("--target", default=".mcp.json", type=Path)
    p.add_argument("--overwrite", action="store_true", help="replace servers that already exist")
    p.add_argument("--list", action="store_true")
    a = p.parse_args(argv)
    if a.list or not a.profiles:
        print("\n".join(available()))
        return 0
    added, skipped, notes = merge(a.target, a.profiles, a.overwrite)
    print(f"added: {', '.join(added) or '-'}; kept existing: {', '.join(skipped) or '-'} -> {a.target}")
    for n in notes:
        print(f"note  {n}")
    print("Set any ${VAR} referenced above in your environment, then restart the client / run `claude mcp list`.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Repository checks for QA Forge: manifests, frontmatter, cross-references, MCP profiles, secrets.

Run from the repo root: python scripts/validate_plugin.py   (exit 1 on any error)
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "qa-forge"
SKILL = PLUGIN / "skills" / "qa-forge"
SECRET = re.compile(r"(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|xox[bp]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}|ATATT[A-Za-z0-9_\-=]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)")
errors = []


def err(msg):
    errors.append(msg)


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        err(f"{path.relative_to(ROOT)}: invalid JSON ({e})")
        return {}


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        err(f"{path.relative_to(ROOT)}: missing YAML frontmatter")
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"')
    return fm, text


def main():
    # manifests
    market = load(ROOT / ".claude-plugin" / "marketplace.json")
    manifest = load(PLUGIN / ".claude-plugin" / "plugin.json")
    for key in ("name", "owner", "plugins"):
        if key not in market:
            err(f"marketplace.json: missing '{key}'")
    for p in market.get("plugins", []):
        src = ROOT / p.get("source", "")
        if not (src / ".claude-plugin" / "plugin.json").exists():
            err(f"marketplace.json: plugin '{p.get('name')}' source {p.get('source')} has no plugin.json")
    if not re.fullmatch(r"[a-z0-9-]+", manifest.get("name", "")):
        err("plugin.json: name must be kebab-case")
    versions = {manifest.get("version")} | {p.get("version") for p in market.get("plugins", []) if p.get("name") == manifest.get("name")}
    if len(versions - {None}) > 1:
        err(f"version mismatch between plugin.json and marketplace.json: {versions}")
    mcp = load(PLUGIN / ".mcp.json")
    for name, spec in mcp.get("mcpServers", {}).items():
        if "env" in spec or "headers" in spec:
            err(f".mcp.json: default server '{name}' needs credentials; move it to mcp-profiles/")

    # skill
    fm, body = frontmatter(SKILL / "SKILL.md")
    if fm.get("name") != "qa-forge":
        err("SKILL.md: name must be qa-forge")
    if not (50 <= len(fm.get("description", "")) <= 1024):
        err("SKILL.md: description must be 50-1024 chars")
    if len(body.splitlines()) > 500:
        err("SKILL.md: keep under 500 lines; move detail to references/")

    # cross references from SKILL.md, references, commands, agents
    docs = [SKILL / "SKILL.md", *SKILL.glob("references/*.md"), *PLUGIN.glob("commands/*.md"), *PLUGIN.glob("agents/*.md")]
    ref = re.compile(r"(?:\$\{CLAUDE_PLUGIN_ROOT\}/skills/qa-forge/|`)((?:references|templates|schemas|scripts|mcp-profiles)/[A-Za-z0-9_.\-]+\.(?:md|json|py))")
    for d in docs:
        for target in set(ref.findall(d.read_text(encoding="utf-8"))):
            if not (SKILL / target).exists():
                err(f"{d.relative_to(ROOT)}: references missing file {target}")
    for script in re.findall(r"`([a-z_]+\.py)`", (SKILL / "SKILL.md").read_text()):
        if not (SKILL / "scripts" / script).exists():
            err(f"SKILL.md: lists missing script {script}")

    # commands & agents
    for c in PLUGIN.glob("commands/*.md"):
        cfm, _ = frontmatter(c)
        if not cfm.get("description"):
            err(f"{c.relative_to(ROOT)}: missing description")
    for a in PLUGIN.glob("agents/*.md"):
        afm, _ = frontmatter(a)
        if afm.get("name") != a.stem or not afm.get("description"):
            err(f"{a.relative_to(ROOT)}: name must equal file name and description is required")

    # MCP profiles
    for prof in (SKILL / "mcp-profiles").glob("*.json"):
        data = load(prof)
        servers = data.get("mcpServers")
        if not servers:
            err(f"{prof.relative_to(ROOT)}: no mcpServers")
        for name, spec in (servers or {}).items():
            if not ("command" in spec or "url" in spec):
                err(f"{prof.relative_to(ROOT)}: server '{name}' needs command or url")
            for k, v in {**spec.get("env", {}), **spec.get("headers", {})}.items():
                if v and "${" not in v and k.upper() not in ("READ_ONLY_MODE", "AZURE_DEVOPS_AUTH_METHOD"):
                    err(f"{prof.relative_to(ROOT)}: {name}.{k} must reference an env var (${{VAR}}), not a literal")

    # secrets anywhere
    for f in ROOT.rglob("*"):
        if f.is_file() and ".git" not in f.parts and f.suffix in {".md", ".json", ".py", ".yml", ".yaml", ".txt", ".xml"}:
            if SECRET.search(f.read_text(encoding="utf-8", errors="ignore")):
                err(f"{f.relative_to(ROOT)}: looks like it contains a secret")

    for e in errors:
        print(f"ERROR {e}")
    print(f"validate_plugin: {'FAILED' if errors else 'OK'} ({len(errors)} errors)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

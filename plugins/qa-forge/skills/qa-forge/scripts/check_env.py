#!/usr/bin/env python3
"""Report which QA Forge integrations look configured. Prints env var NAMES only, never values."""
import argparse
import json
import os
import shutil
import sys

INTEGRATIONS = {
    "Jira Cloud (Rovo MCP, API token mode)": {"any": [["ATLASSIAN_BASIC_AUTH"], ["ATLASSIAN_API_KEY"], ["ATLASSIAN_EMAIL", "ATLASSIAN_API_TOKEN"]]},
    "Jira self-hosted (mcp-atlassian)": {"any": [["JIRA_URL", "JIRA_PERSONAL_TOKEN"], ["JIRA_URL", "JIRA_USERNAME", "JIRA_API_TOKEN"]]},
    "Azure DevOps (envvar token)": {"any": [["ADO_MCP_AUTH_TOKEN"], ["AZURE_DEVOPS_EXT_PAT"]]},
    "Azure DevOps on-prem (PAT)": {"any": [["AZURE_DEVOPS_ORG_URL", "AZURE_DEVOPS_PAT"]]},
    "BrowserStack": {"any": [["BROWSERSTACK_USERNAME", "BROWSERSTACK_ACCESS_KEY"]]},
    "Postman": {"any": [["POSTMAN_API_KEY"]]},
    "TestRail": {"any": [["TESTRAIL_URL", "TESTRAIL_USERNAME", "TESTRAIL_API_KEY"]]},
    "GitHub": {"any": [["GITHUB_PERSONAL_ACCESS_TOKEN"], ["GITHUB_TOKEN"], ["GH_TOKEN"]]},
    "Appium (Android SDK)": {"any": [["ANDROID_HOME"], ["ANDROID_SDK_ROOT"]]},
}
CLIS = {
    "npx": "Node MCP servers (Playwright, ADO, Appium, BrowserStack)",
    "uvx": "Python MCP servers (mcp-atlassian)",
    "az": "Azure CLI auth for ADO MCP (--authentication azcli)",
    "gh": "GitHub CLI",
    "docker": "Containerised MCP servers",
    "java": "Appium / Selenium",
    "adb": "Android devices/emulators",
    "xcrun": "iOS simulators (macOS)",
}


def check(env):
    out = []
    for name, spec in INTEGRATIONS.items():
        found = next((combo for combo in spec["any"] if all(env.get(v) for v in combo)), None)
        out.append({
            "integration": name,
            "configured": bool(found),
            "vars": found or spec["any"][0],
        })
    clis = [{"cli": c, "present": shutil.which(c) is not None, "used_for": why} for c, why in CLIS.items()]
    return out, clis


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", action="store_true", help="machine-readable output")
    a = p.parse_args(argv)
    integ, clis = check(os.environ)
    if a.json:
        print(json.dumps({"integrations": integ, "clis": clis}, indent=2))
        return 0
    print("| Integration | Credentials | Env vars |\n|---|---|---|")
    for r in integ:
        print(f"| {r['integration']} | {'set' if r['configured'] else 'missing'} | {', '.join(r['vars'])} |")
    print("\n| CLI | Present | Used for |\n|---|---|---|")
    for c in clis:
        print(f"| {c['cli']} | {'yes' if c['present'] else 'no'} | {c['used_for']} |")
    print("\nOAuth-based connections (Jira Rovo OAuth, ADO interactive/azcli) don't use env vars - check the MCP tool list instead.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

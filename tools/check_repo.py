#!/usr/bin/env python3
"""Repository consistency checks (standard library only). Run before committing and in CI.

    python3 tools/check_repo.py            # all checks
    python3 tools/check_repo.py --tag v2.0.0   # also require the tag to match the version

Checks:
  1. Manifests are valid JSON and plugin.json, marketplace.json and CHANGELOG.md agree on
     the version.
  2. SKILL.md frontmatter uses only portable keys, the name matches the folder, and the
     description and body stay within the documented size limits.
  3. Every references/ or scripts/ file named in SKILL.md exists, and every reference file
     is named in SKILL.md.
  4. Each eval case with a "calc" block reproduces its numeric "expect" values through
     compute_tax, so eval figures cannot drift from the calculator.
  5. The calculator self-test passes.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "bd-income-tax"

# Keys accepted when a skill is uploaded to claude.ai / desktop apps.
PORTABLE_FRONTMATTER_KEYS = {
    "name", "description", "license", "compatibility", "metadata", "allowed-tools",
}
MAX_DESCRIPTION_CHARS = 1024
MAX_SKILL_BODY_LINES = 500

errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)
    print(f"  [FAIL] {message}")


def ok(message: str) -> None:
    print(f"  [ OK ] {message}")


def load_calculator():
    spec = importlib.util.spec_from_file_location("tax_calc", SKILL / "scripts" / "tax_calc.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_versions(tag: str | None) -> None:
    print("Versions")
    try:
        plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text("utf-8"))
        market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text("utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"manifest unreadable: {exc}")
        return
    plugin_version = plugin.get("version")
    market_version = market.get("metadata", {}).get("version")
    match = re.search(r"^## \[(\d+\.\d+\.\d+)\]", (ROOT / "CHANGELOG.md").read_text("utf-8"), re.M)
    changelog_version = match.group(1) if match else None
    versions = {
        "plugin.json": plugin_version,
        "marketplace.json": market_version,
        "CHANGELOG.md (top entry)": changelog_version,
    }
    if len(set(versions.values())) == 1 and plugin_version:
        ok(f"all three agree on {plugin_version}")
    else:
        fail(f"version mismatch: {versions}")
    if tag is not None:
        if tag == f"v{plugin_version}":
            ok(f"tag {tag} matches the version")
        else:
            fail(f"tag {tag!r} does not match version v{plugin_version}")


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Minimal parser for the flat frontmatter this skill uses (top-level keys, folded
    scalars, one nested mapping). Returns ({key: value}, body)."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.index("\n---\n", 4)
    block, body = text[4:end], text[end + 5:]
    data: dict = {}
    key = None
    for line in block.splitlines():
        top = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if top:
            key, value = top.group(1), top.group(2).strip()
            data[key] = "" if value in (">-", ">", "|", "|-") else value
        elif key is not None and line.strip():
            data[key] = (data[key] + " " + line.strip()).strip()
    return data, body


def check_skill_md() -> None:
    print("SKILL.md")
    text = (SKILL / "SKILL.md").read_text("utf-8")
    front, body = parse_frontmatter(text)
    if not front:
        fail("no frontmatter found")
        return
    extra = set(front) - PORTABLE_FRONTMATTER_KEYS
    if extra:
        fail(f"non-portable frontmatter keys (rejected on upload): {sorted(extra)}")
    else:
        ok(f"frontmatter keys are portable: {sorted(front)}")
    if front.get("name") != SKILL.name:
        fail(f"name {front.get('name')!r} does not match folder {SKILL.name!r}")
    description = front.get("description", "")
    if not description:
        fail("description is empty")
    elif len(description) > MAX_DESCRIPTION_CHARS:
        fail(f"description is {len(description)} chars (limit {MAX_DESCRIPTION_CHARS})")
    else:
        ok(f"description is {len(description)} chars (limit {MAX_DESCRIPTION_CHARS})")
    body_lines = body.count("\n") + 1
    if body_lines > MAX_SKILL_BODY_LINES:
        fail(f"body is {body_lines} lines (limit {MAX_SKILL_BODY_LINES})")
    else:
        ok(f"body is {body_lines} lines (limit {MAX_SKILL_BODY_LINES})")

    mentioned = set(re.findall(r"`((?:references|scripts)/[\w./-]+)`", text))
    missing = sorted(p for p in mentioned if not (SKILL / p).is_file())
    if missing:
        fail(f"SKILL.md names files that do not exist: {missing}")
    else:
        ok(f"all {len(mentioned)} files named in SKILL.md exist")
    unlinked = sorted(
        f"references/{p.name}" for p in (SKILL / "references").glob("*.md")
        if f"references/{p.name}" not in mentioned
    )
    if unlinked:
        fail(f"reference files not named in SKILL.md: {unlinked}")
    else:
        ok("every reference file is named in SKILL.md")


def check_evals(calc) -> None:
    print("Evals")
    try:
        data = json.loads((SKILL / "evals" / "evals.json").read_text("utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"evals.json unreadable: {exc}")
        return
    ids = [case.get("id") for case in data.get("cases", [])]
    if len(ids) != len(set(ids)):
        fail("duplicate eval case ids")
    checked = 0
    for case in data.get("cases", []):
        if "calc" not in case:
            continue
        try:
            result = calc.compute_tax(**case["calc"])
        except Exception as exc:  # noqa: BLE001 - report any calculator failure
            fail(f"{case['id']}: compute_tax raised {exc!r}")
            continue
        for field, expected in case.get("expect", {}).items():
            if field == "notes":
                continue
            if field not in result:
                fail(f"{case['id']}: calculator has no field {field!r}")
                continue
            got = result[field]
            if isinstance(expected, (int, float)) and not isinstance(expected, bool):
                good = abs(got - expected) <= 1
            else:
                good = got == expected
            if not good:
                fail(f"{case['id']}: {field} expected {expected!r}, calculator gives {got!r}")
        checked += 1
    ok(f"{checked} of {len(ids)} eval cases checked against the calculator")


def check_selftest(calc) -> None:
    print("Calculator self-test")
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        failures = calc._selftest()
    if failures:
        print(buffer.getvalue())
        fail(f"{failures} self-test check(s) failed")
    else:
        ok(f"{buffer.getvalue().count('[PASS]')} checks passed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tag", help="release tag to compare with the version, e.g. v2.0.0")
    args = parser.parse_args()

    check_versions(args.tag)
    check_skill_md()
    calc = load_calculator()
    check_evals(calc)
    check_selftest(calc)

    print()
    if errors:
        print(f"{len(errors)} problem(s) found.")
        return 1
    print("All repository checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

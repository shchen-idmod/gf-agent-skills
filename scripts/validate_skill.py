#!/usr/bin/env python3
"""
validate_skill.py — Validate all SKILL.md files in the repo.

Checks:
  - SKILL.md exists and has required sections
  - Frontmatter has required fields with valid values
  - evals/evals.json present for all skills (errors if missing)
"""

import json
import re
import sys
import yaml
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).parent.parent

REQUIRED_FRONTMATTER = ["name", "description", "owner", "version"]
REQUIRED_SECTIONS = [
    "## Instructions",
    "## Output Format",
    "## Limitations",
]

errors = []
warnings = []


def find_skill_dirs():
    return sorted([
        p.parent for p in REPO_ROOT.rglob("SKILL.md")
    ])


def parse_frontmatter(path: Path):
    text = path.read_text()
    parts = text.split("---", 2)
    if len(parts) < 3:
        errors.append(f"[{path.parent.name}] SKILL.md missing frontmatter (no --- delimiters)")
        return None
    try:
        return yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        errors.append(f"[{path.parent.name}] Frontmatter YAML parse error: {e}")
        return None


def validate_frontmatter(skill_dir: Path, fm: dict):
    for field in REQUIRED_FRONTMATTER:
        if not fm.get(field):
            errors.append(f"[{skill_dir.name}] Missing required frontmatter field: '{field}'")



def validate_skill_md(skill_dir: Path):
    path = skill_dir / "SKILL.md"
    content = path.read_text()

    for section in REQUIRED_SECTIONS:
        if section not in content:
            errors.append(f"[{skill_dir.name}] SKILL.md missing required section: '{section}'")

    if len(content.strip()) < 300:
        warnings.append(f"[{skill_dir.name}] SKILL.md seems very short — is it complete?")


def validate_evals(skill_dir: Path, fm: dict):
    evals_path = skill_dir / "evals" / "evals.json"

    if not evals_path.exists():
        errors.append(
            f"[{skill_dir.name}] Missing evals/evals.json — required for all skills. "
            "See evals/README.md for the schema."
        )
        return

    try:
        data = json.loads(evals_path.read_text())
    except json.JSONDecodeError as e:
        errors.append(f"[{skill_dir.name}] evals/evals.json parse error: {e}")
        return

    if not isinstance(data.get("evals"), list) or len(data["evals"]) == 0:
        errors.append(f"[{skill_dir.name}] evals/evals.json must have a non-empty 'evals' array")
    else:
        for i, ev in enumerate(data["evals"]):
            for req in ["id", "name", "prompt", "rubric"]:
                if req not in ev:
                    errors.append(f"[{skill_dir.name}] evals[{i}] missing field '{req}'")


def main():
    skill_dirs = find_skill_dirs()

    if not skill_dirs:
        print("No SKILL.md files found.")
        sys.exit(0)

    print(f"Validating {len(skill_dirs)} skill(s)...\n")

    for skill_dir in skill_dirs:
        skill_md = skill_dir / "SKILL.md"
        fm = parse_frontmatter(skill_md)
        if fm:
            validate_frontmatter(skill_dir, fm)
            validate_evals(skill_dir, fm)
        validate_skill_md(skill_dir)

    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  ⚠  {w}")
        print()

    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  ✗  {e}")
        print(f"\n{len(errors)} error(s). Fix before merging.")
        sys.exit(1)
    else:
        print(f"✓  All {len(skill_dirs)} skill(s) passed validation.")
        if warnings:
            print(f"   {len(warnings)} warning(s) to review.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
deploy.py — Validate and package GF Foundation Skills

Validation (default — runs when no mode flag is given):

  python scripts/deploy.py                                      # all skills
  python scripts/deploy.py --plugin foundation-wide             # one plugin
  python scripts/deploy.py --plugin idm --skill disease-modeling-review

Packaging (Claude.ai only — skills must be uploaded as ZIPs via the UI):

  python scripts/deploy.py --package --plugin foundation-wide
  python scripts/deploy.py --package --plugin idm
"""

import argparse
import json
import sys
import yaml
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

PLUGINS = {
    "foundation-wide":      REPO_ROOT / "foundation-wide",
    "idm":                  REPO_ROOT / "groups" / "idm",
    "global-health":        REPO_ROOT / "groups" / "global-health",
    "global-development":   REPO_ROOT / "groups" / "global-development",
    "policy":               REPO_ROOT / "groups" / "policy",
    "finance":              REPO_ROOT / "groups" / "finance",
    "it":                   REPO_ROOT / "groups" / "it",
}

REQUIRED_FRONTMATTER = ["name", "description", "owner", "version"]
# ## Instructions — hard error always
REQUIRED_SECTIONS_ALL = ["## Instructions"]
# ## Output Format — hard error for foundation-wide, ignored for group
REQUIRED_SECTIONS_FOUNDATION = ["## Output Format"]
# ## Limitations — warning only, never a hard error
RECOMMENDED_SECTIONS = ["## Limitations"]


# ── Helpers ────────────────────────────────────────────────────────────────

def get_skills(plugin_path: Path, skill_filter: str = None) -> list[Path]:
    """
    Find all skill dirs (containing SKILL.md) under a plugin's skills/ folder.
    Handles both flat layout (skills/my-skill/) and
    category layout (skills/research/my-skill/).
    """
    skills_root = plugin_path / "skills"
    if not skills_root.exists():
        return []

    found = []
    for path in sorted(skills_root.rglob("SKILL.md")):
        skill_dir = path.parent
        if skill_dir not in found:
            found.append(skill_dir)

    if skill_filter:
        found = [s for s in found if s.name == skill_filter]

    return found


def ok(msg):   print(f"  ✓  {msg}")
def warn(msg): print(f"  ⚠  {msg}")
def err(msg):  print(f"  ✗  {msg}")


# ── Validation ─────────────────────────────────────────────────────────────

def validate_skill(skill_dir: Path) -> tuple[list, list]:
    errors, warnings = [], []
    skill_md = skill_dir / "SKILL.md"

    text = skill_md.read_text()
    parts = text.split("---", 2)
    if len(parts) < 3:
        errors.append("Missing frontmatter (no --- delimiters)")
        return errors, warnings

    try:
        fm = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        errors.append(f"Frontmatter YAML parse error: {e}")
        return errors, warnings

    for field in REQUIRED_FRONTMATTER:
        if not fm.get(field):
            errors.append(f"Missing required frontmatter field: '{field}'")

    body = parts[2]
    is_foundation_wide = "foundation-wide" in skill_dir.parts

    # ## Instructions — hard error for all skills
    for section in REQUIRED_SECTIONS_ALL:
        if section not in body:
            errors.append(f"Missing required section: '{section}'")

    # ## Output Format — hard error for foundation-wide only
    if is_foundation_wide:
        for section in REQUIRED_SECTIONS_FOUNDATION:
            if section not in body:
                errors.append(f"Missing required section for foundation-wide skills: '{section}'")

    # ## Limitations — warning only
    for section in RECOMMENDED_SECTIONS:
        if section not in body:
            warnings.append(f"Recommended section missing: '{section}' (not required but strongly encouraged)")


    evals_path = skill_dir / "evals" / "evals.json"
    if is_foundation_wide and not evals_path.exists():
        warnings.append("Foundation-wide skill has no evals/evals.json — skill is Provisional")
    elif evals_path.exists():
        try:
            data = json.loads(evals_path.read_text())
            if not isinstance(data.get("evals"), list) or len(data["evals"]) == 0:
                errors.append("evals/evals.json must have a non-empty 'evals' array")
        except json.JSONDecodeError as e:
            errors.append(f"evals/evals.json parse error: {e}")

    return errors, warnings


def run_validate(plugin_name: str = None, skill_filter: str = None):
    plugins = {plugin_name: PLUGINS[plugin_name]} if plugin_name else PLUGINS

    total_errors, total_warnings, total_skills = 0, 0, 0

    for pname, plugin_path in plugins.items():
        skills = get_skills(plugin_path, skill_filter)
        if not skills:
            continue

        print(f"\n── {pname} ({len(skills)} skill(s)) ──")
        for skill_dir in skills:
            total_skills += 1
            # Show category/skill-name for nested layout
            rel = skill_dir.relative_to(plugin_path / "skills")
            label = str(rel)

            errors, warnings = validate_skill(skill_dir)
            total_errors += len(errors)
            total_warnings += len(warnings)

            if errors or warnings:
                print(f"\n  {label}")
                for e in errors:   err(e)
                for w in warnings: warn(w)
            else:
                ok(label)

    print()
    if total_skills == 0:
        print("No skills found.")
        return

    if total_errors:
        print(f"✗  {total_errors} error(s) found. Fix before merging.")
        sys.exit(1)
    else:
        msg = f"✓  All {total_skills} skill(s) passed validation."
        if total_warnings:
            msg += f" ({total_warnings} warning(s) to review.)"
        print(msg)


# ── Claude.ai packaging ────────────────────────────────────────────────────

def run_package(plugin_name: str, skill_filter: str = None):
    plugin_path = PLUGINS[plugin_name]
    skills = get_skills(plugin_path, skill_filter)

    if not skills:
        print(f"No skills found in plugin '{plugin_name}'")
        sys.exit(1)

    print(f"\nValidating before packaging...\n")
    has_errors = False
    for skill_dir in skills:
        errors, _ = validate_skill(skill_dir)
        if errors:
            err(f"{skill_dir.name}: {len(errors)} error(s)")
            for e in errors: print(f"       {e}")
            has_errors = True
    if has_errors:
        print("\nFix errors before packaging.")
        sys.exit(1)
    print("  All skills valid.\n")

    output_dir = REPO_ROOT / "dist" / "claude-ai"
    output_dir.mkdir(parents=True, exist_ok=True)

    for old_zip in output_dir.glob("*.zip"):
        old_zip.unlink()

    print(f"Packaging {len(skills)} skill(s) → {output_dir}\n")

    for skill_dir in skills:
        zip_path = output_dir / f"{skill_dir.name}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in skill_dir.rglob("*"):
                if file_path.is_file():
                    arcname = skill_dir.name / file_path.relative_to(skill_dir)
                    zf.write(file_path, arcname)
        size_kb = zip_path.stat().st_size / 1024
        ok(f"{skill_dir.name}.zip  ({size_kb:.1f} KB)")

    print(f"""
── Upload to Claude.ai ─────────────────────────────────────────────────────

Personal:
  claude.ai → Settings → Customize → Skills → Upload skill
  Upload each .zip from: {output_dir}

Team / Enterprise (org-wide):
  claude.ai → Organization Settings → Skills → Upload skill
  Upload each .zip, then toggle ON to provision to all members

────────────────────────────────────────────────────────────────────────────
""")


# ── CLI ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Validate and package GF Foundation Skills")

    mode = parser.add_mutually_exclusive_group(required=False)
    mode.add_argument("--validate", action="store_true",
                      help="Validate skill structure (default when no mode given)")
    mode.add_argument("--package", action="store_true",
                      help="Package skills as ZIPs for Claude.ai upload")

    parser.add_argument("--plugin", choices=list(PLUGINS.keys()),
                        help="Target a specific plugin (default: all)")
    parser.add_argument("--skill", default=None,
                        help="Target a single skill by name")

    args = parser.parse_args()

    if args.package and not args.plugin:
        parser.error("--package requires --plugin")

    if args.package:
        run_package(args.plugin, args.skill)
    else:
        run_validate(args.plugin, args.skill)


if __name__ == "__main__":
    main()

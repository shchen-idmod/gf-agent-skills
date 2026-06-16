#!/usr/bin/env python3
"""
run_evals.py — Run evals.json against a live Claude model to validate skill behaviour.

Requires ANTHROPIC_API_KEY environment variable.

Usage:
  # Run all evals across all skills
  python scripts/run_evals.py

  # Run evals for a specific plugin
  python scripts/run_evals.py --plugin foundation-wide
  python scripts/run_evals.py --plugin idm

  # Run evals for a specific skill
  python scripts/run_evals.py --plugin idm --skill idm-pkg-install

  # Run a single eval by ID
  python scripts/run_evals.py --plugin idm --skill idm-pkg-install --eval-id pkg-001

  # Use a different model
  python scripts/run_evals.py --model claude-haiku-4-5-20251001

  # Show full responses (default: show summary only)
  python scripts/run_evals.py --verbose

  # Save results to a JSON file
  python scripts/run_evals.py --output results.json

  # Only run evals for skills changed vs main (for CI)
  python scripts/run_evals.py --changed-from origin/main

  # Override with a fixture file instead of evals.json (dev / PII testing)
  python scripts/run_evals.py --plugin idm --skill idm-pkg-install --fixture pii_test_cases.json

  # Use real data from env var and mask PII in saved results
  python scripts/run_evals.py --plugin idm --skill idm-pkg-install --real --mask-output --output results.json

NOTE: This script calls the Anthropic API for every eval case. Each call costs tokens.
      Run targeted evals during development; run all evals before merging to main.
"""

import argparse
from collections import defaultdict
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic package not installed. Run: pip install anthropic")
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Run: pip install pyyaml")
    sys.exit(1)

REPO_ROOT = Path(__file__).parent.parent

# Optional: PII masking from scripts/utils.py (used with --mask-output)
try:
    from utils import SensitiveDataMasker
except ImportError:
    SensitiveDataMasker = None

PLUGINS = {
    "foundation-wide":    REPO_ROOT / "foundation-wide",
    "idm":                REPO_ROOT / "groups" / "idm",
    "global-health":      REPO_ROOT / "groups" / "global-health",
    "global-development": REPO_ROOT / "groups" / "global-development",
    "policy":             REPO_ROOT / "groups" / "policy",
    "finance":            REPO_ROOT / "groups" / "finance",
    "it":                 REPO_ROOT / "groups" / "it",
}


def get_changed_skills(base_ref: str) -> list[tuple[str, str]]:
    """Return [(plugin_name, skill_name), ...] for skills with files changed vs base_ref."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
            capture_output=True, text=True, check=True,
            cwd=str(REPO_ROOT),
        )
    except subprocess.CalledProcessError as e:
        sys.exit(f"ERROR: git diff failed for ref '{base_ref}'. Is this a git repo?\n{e.stderr.strip()}")
    changed_files = [REPO_ROOT / f for f in result.stdout.strip().splitlines() if f]

    found: set[tuple[str, str]] = set()
    for filepath in changed_files:
        if not filepath.is_relative_to(REPO_ROOT):
            continue
        current = filepath.parent
        while current != REPO_ROOT and current.parent != current:
            if (current / "SKILL.md").exists():
                skill_name = current.name
                for pname, ppath in PLUGINS.items():
                    try:
                        current.relative_to(ppath)
                        found.add((pname, skill_name))
                        break
                    except ValueError:
                        continue
                break
            current = current.parent

    return list(found)


def _read_fixture(path: Path) -> list[dict]:
    """Read a fixture file, normalising wrapped {evals:[...]} or bare [...] format."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("evals", data)
    if not isinstance(data, list):
        raise ValueError(f"Fixture at {path} must be a JSON array or {{\"evals\":[...]}} object")
    return data


def _legacy_to_rubric(expected: dict) -> dict:
    """Convert eval_runner.py legacy expected-dict format to rubric format."""
    rubric: dict = {}
    if "risk_level" in expected:
        rubric["must_include_one_of"] = [expected["risk_level"]]
    if "fields_flagged" in expected:
        rubric["must_include"] = list(expected["fields_flagged"])
    if expected.get("pii_detected") is False:
        rubric.setdefault("must_not_include", []).append("pii detected")
    return rubric


DEFAULT_MODEL = "claude-sonnet-4-6"
PASS  = "PASS"
FAIL  = "FAIL"
ERROR = "ERROR"


# ── Helpers ────────────────────────────────────────────────────────────────

def ok(msg):    print(f"  ✓  {msg}")
def fail(msg):  print(f"  ✗  {msg}")
def warn(msg):  print(f"  ⚠  {msg}")
def info(msg):  print(f"  →  {msg}")


def get_skills(plugin_path: Path, skill_filter: str = None) -> list[Path]:
    skills_root = plugin_path / "skills"
    if not skills_root.exists():
        return []
    found = sorted([p.parent for p in skills_root.rglob("SKILL.md")])
    if skill_filter:
        found = [s for s in found if s.name == skill_filter]
    return found


def load_skill_md(skill_dir: Path) -> str:
    return (skill_dir / "SKILL.md").read_text()


def load_evals(
    skill_dir: Path,
    fixture: str | None = None,
    use_real: bool = False,
) -> dict | None:
    # Real data via env var (requires TEST_REAL_FIXTURES_PATH)
    if use_real:
        real_path_str = os.environ.get("TEST_REAL_FIXTURES_PATH")
        if real_path_str:
            print("[real data] ⚠  Loading from TEST_REAL_FIXTURES_PATH — ensure logs are not stored")
            return {"evals": _read_fixture(Path(real_path_str))}
        warn("--real set but TEST_REAL_FIXTURES_PATH is not in env; falling back to evals.json")

    # Named fixture file (absolute path, or filename searched in evals/fixtures/)
    if fixture:
        direct = Path(fixture).resolve()
        if direct.exists():
            return {"evals": _read_fixture(direct)}
        for subdir in ("synthetic", "real"):
            candidate = REPO_ROOT / "evals" / "fixtures" / subdir / fixture
            if candidate.exists():
                return {"evals": _read_fixture(candidate)}
        raise FileNotFoundError(
            f"Fixture '{fixture}' not found at absolute path or in "
            "evals/fixtures/synthetic/ or evals/fixtures/real/"
        )

    # Default: skill's own evals/evals.json
    evals_path = skill_dir / "evals" / "evals.json"
    if not evals_path.exists():
        return None
    return json.loads(evals_path.read_text())


def parse_frontmatter(skill_md: str) -> dict:
    parts = skill_md.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}


# ── Rubric checker ─────────────────────────────────────────────────────────

def check_rubric(response_text: str, rubric: dict) -> tuple[str, list[str]]:
    """
    Evaluate a response against a rubric. Returns (PASS|FAIL, [reasons]).

    Supported rubric fields:
      pass_condition        — human-readable description (not machine-checked)
      must_include          — list of strings ALL must appear in response
      must_include_one_of   — list of strings, at least ONE must appear
      must_include_all      — alias for must_include
      must_not_include      — list of strings NONE must appear in response
      required_sections     — list of strings ALL must appear (same as must_include)
    """
    reasons = []
    text_lower = response_text.lower()

    # must_include / must_include_all / required_sections
    for field in ["must_include", "must_include_all", "required_sections"]:
        for term in rubric.get(field, []):
            if term.lower() not in text_lower:
                reasons.append(f"missing required: '{term}'")

    # must_include_one_of
    one_of = rubric.get("must_include_one_of", [])
    if one_of:
        if not any(term.lower() in text_lower for term in one_of):
            reasons.append(f"must include at least one of: {one_of}")

    # must_include_groups (list of one-of groups — each group requires at least one match)
    for group in rubric.get("must_include_groups", []):
        if not any(term.lower() in text_lower for term in group):
            reasons.append(f"must include at least one of: {group}")

    # must_not_include
    for term in rubric.get("must_not_include", []):
        if term.lower() in text_lower:
            reasons.append(f"must NOT include: '{term}'")

    status = FAIL if reasons else PASS
    return status, reasons


# ── Single eval runner ─────────────────────────────────────────────────────

def run_eval(
    client: anthropic.Anthropic,
    skill_name: str,
    skill_md: str,
    eval_case: dict,
    model: str,
    verbose: bool,
    masker=None,
) -> dict:
    eval_id    = eval_case["id"]
    eval_name  = eval_case["name"]
    input_text = eval_case["prompt"]

    # Resolve rubric — supports new `rubric` key, nested `expected.rubric`, and legacy flat `expected`
    rubric = eval_case.get("rubric") or {}
    if not rubric:
        expected = eval_case.get("expected") or {}
        if isinstance(expected, dict):
            rubric = expected.get("rubric") or _legacy_to_rubric(expected)

    started_at = time.time()

    try:
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            temperature=0,
            system=skill_md,
            messages=[{"role": "user", "content": input_text}]
        )
        response_text = response.content[0].text
        elapsed = round(time.time() - started_at, 1)

        status, reasons = check_rubric(response_text, rubric)

        if verbose:
            print(f"\n    Input:    {input_text}")
            print(f"    Response: {response_text[:300]}{'...' if len(response_text) > 300 else ''}")
            if reasons:
                for r in reasons:
                    print(f"    Reason:   {r}")

        safe_response = masker.mask_string(response_text) if masker else response_text

        return {
            "eval_id":       eval_id,
            "eval_name":     eval_name,
            "status":        status,
            "reasons":       reasons,
            "elapsed_s":     elapsed,
            "prompt":        input_text,
            "response":      safe_response,
            "pass_condition": rubric.get("pass_condition", "")
        }

    except Exception as e:
        elapsed = round(time.time() - started_at, 1)
        return {
            "eval_id":   eval_id,
            "eval_name": eval_name,
            "status":    ERROR,
            "reasons":   [str(e)],
            "elapsed_s": elapsed,
            "prompt":    input_text,
            "response":  ""
        }


# ── Skill eval runner ──────────────────────────────────────────────────────

def run_skill_evals(
    client: anthropic.Anthropic,
    skill_dir: Path,
    plugin_name: str,
    model: str,
    eval_id_filter: str | None,
    verbose: bool,
    fixture: str | None = None,
    use_real: bool = False,
    masker=None,
) -> dict:
    skill_md   = load_skill_md(skill_dir)
    fm         = parse_frontmatter(skill_md)
    skill_name = fm.get("name", skill_dir.name)
    evals_data = load_evals(skill_dir, fixture=fixture, use_real=use_real)

    rel = skill_dir.relative_to(
        PLUGINS[plugin_name] / "skills"
    )

    if evals_data is None:
        warn(f"{rel} — no evals/evals.json, skipping")
        return {"skill": skill_name, "skipped": True, "results": []}

    eval_cases = evals_data.get("evals", [])
    if eval_id_filter:
        eval_cases = [e for e in eval_cases if e["id"] == eval_id_filter]
        if not eval_cases:
            warn(f"{rel} — eval ID '{eval_id_filter}' not found")
            return {"skill": skill_name, "skipped": True, "results": []}

    print(f"\n  {rel}  ({len(eval_cases)} eval(s))")

    results = []
    for ev in eval_cases:
        result = run_eval(client, skill_name, skill_md, ev, model, verbose, masker=masker)
        results.append(result)

        if result["status"] == PASS:
            ok(f"{ev['id']}  {ev['name']}  ({result['elapsed_s']}s)")
        elif result["status"] == FAIL:
            fail(f"{ev['id']}  {ev['name']}  ({result['elapsed_s']}s)")
            for r in result["reasons"]:
                print(f"       → {r}")
        else:
            warn(f"{ev['id']}  {ev['name']}  ERROR: {result['reasons'][0]}")

    passed  = sum(1 for r in results if r["status"] == PASS)
    failed  = sum(1 for r in results if r["status"] == FAIL)
    errored = sum(1 for r in results if r["status"] == ERROR)

    return {
        "skill":   skill_name,
        "path":    str(rel),
        "skipped": False,
        "passed":  passed,
        "failed":  failed,
        "errored": errored,
        "total":   len(results),
        "results": results
    }


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Run evals.json against a live Claude model to validate skill behaviour"
    )
    parser.add_argument("--plugin",   choices=list(PLUGINS.keys()),
                        help="Target a specific plugin (default: all)")
    parser.add_argument("--skill",    default=None,
                        help="Target a single skill by name")
    parser.add_argument("--eval-id",  default=None,
                        help="Run a single eval case by ID (e.g. pkg-001)")
    parser.add_argument("--model",    default=DEFAULT_MODEL,
                        help=f"Anthropic model to use (default: {DEFAULT_MODEL})")
    parser.add_argument("--verbose",  action="store_true",
                        help="Show full inputs and responses")
    parser.add_argument("--output",   default=None,
                        help="Save full results to a JSON file")
    parser.add_argument(
        "--changed-from",
        default=None,
        metavar="REF",
        help="Only run evals for skills changed vs REF (e.g. origin/main)",
    )
    parser.add_argument(
        "--fixture",
        default=None,
        metavar="FILE",
        help="Override evals source: path to a JSON fixture file, or a filename searched "
             "in evals/fixtures/synthetic/ (requires --plugin and --skill)",
    )
    parser.add_argument(
        "--real",
        action="store_true",
        help="Load real fixtures from TEST_REAL_FIXTURES_PATH env var (requires --plugin and --skill)",
    )
    parser.add_argument(
        "--mask-output",
        action="store_true",
        help="Mask PII patterns in saved --output JSON (uses evals/shared/utils.py)",
    )
    args = parser.parse_args()

    if (args.fixture or args.real) and not (args.plugin and args.skill):
        parser.error("--fixture and --real require --plugin and --skill")

    # Check API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.")
        print("       export ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    masker = None
    if args.mask_output:
        if SensitiveDataMasker is None:
            warn("--mask-output requested but evals/shared/utils.py could not be imported; masking disabled")
        else:
            masker = SensitiveDataMasker()

    print(f"\nRunning evals  model={args.model}  {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n")
    print("─" * 60)

    all_skill_results = []
    total_passed = total_failed = total_errored = total_skipped = 0

    # Build run list and execute evals
    if args.changed_from:
        changed_pairs = get_changed_skills(args.changed_from)
        if not changed_pairs:
            print("No skill changes detected — nothing to eval.")
            sys.exit(0)
        if args.plugin or args.skill:
            warn("--plugin and --skill are ignored when --changed-from is set")
        grouped: dict[str, list[str]] = defaultdict(list)
        for pname, sname in changed_pairs:
            if pname in PLUGINS:
                grouped[pname].append(sname)
        run_list = [(pname, PLUGINS[pname], snames) for pname, snames in grouped.items()]

        for pname, plugin_path, skill_names in run_list:
            skills = []
            for sname in skill_names:
                skills.extend(get_skills(plugin_path, sname))
            if not skills:
                continue

            print(f"\n── {pname} ──")

            for skill_dir in skills:
                result = run_skill_evals(
                    client, skill_dir, pname,
                    args.model, args.eval_id, args.verbose,
                    masker=masker,
                )
                result["plugin"] = pname
                all_skill_results.append(result)

                if result.get("skipped"):
                    total_skipped += 1
                else:
                    total_passed  += result.get("passed", 0)
                    total_failed  += result.get("failed", 0)
                    total_errored += result.get("errored", 0)
    else:
        target_plugins = {args.plugin: PLUGINS[args.plugin]} if args.plugin else PLUGINS
        run_list = [(pname, ppath, args.skill) for pname, ppath in target_plugins.items()]

        for pname, plugin_path, skill_filter in run_list:
            skills = get_skills(plugin_path, skill_filter)
            if not skills:
                continue

            print(f"\n── {pname} ──")

            for skill_dir in skills:
                result = run_skill_evals(
                    client, skill_dir, pname,
                    args.model, args.eval_id, args.verbose,
                    fixture=args.fixture,
                    use_real=args.real,
                    masker=masker,
                )
                result["plugin"] = pname
                all_skill_results.append(result)

                if result.get("skipped"):
                    total_skipped += 1
                else:
                    total_passed  += result.get("passed", 0)
                    total_failed  += result.get("failed", 0)
                    total_errored += result.get("errored", 0)

    # ── Summary ────────────────────────────────────────────────────────────
    total_run = total_passed + total_failed + total_errored
    print(f"\n{'─' * 60}")
    print(f"\nResults:  {total_run} run  "
          f"✓ {total_passed} passed  "
          f"✗ {total_failed} failed  "
          f"⚠ {total_errored} errored  "
          f"— {total_skipped} skipped (no evals)\n")

    # Failed skill summary
    failed_skills = [
        r for r in all_skill_results
        if not r.get("skipped") and (r.get("failed", 0) + r.get("errored", 0)) > 0
    ]
    if failed_skills:
        print("Failed skills:")
        for r in failed_skills:
            print(f"  {r['plugin']}/{r['path']}  "
                  f"({r['failed']} failed, {r['errored']} errored)")
        print()

    # Save output
    if args.output:
        output = {
            "run_at":  datetime.now(timezone.utc).isoformat(),
            "model":   args.model,
            "summary": {
                "passed":  total_passed,
                "failed":  total_failed,
                "errored": total_errored,
                "skipped": total_skipped,
                "total":   total_run
            },
            "skills": all_skill_results
        }
        Path(args.output).write_text(json.dumps(output, indent=2))
        print(f"Results saved to: {args.output}\n")

    sys.exit(1 if (total_failed + total_errored) > 0 else 0)


if __name__ == "__main__":
    main()

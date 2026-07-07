#!/usr/bin/env python3
"""Path-aware approval-count gate for PRs.

GitHub branch protection has a single `required_approving_review_count` per
branch, so it can't require "2 approvals for foundation-wide, 1 for group."
This check does that: it inspects the PR's changed paths, computes the required
count, and fails if there aren't enough distinct approvals.

Division of labor:
- Branch protection `require_code_owner_reviews: true` guarantees at least one
  approval comes from the right CODEOWNERS team.
- This check enforces the *number* of approvals based on path.

LIMITATION (see extension note at bottom): this counts distinct approvers, not
"approvers who are members of the owning team." For foundation-wide the 2nd
approval could currently be anyone. Extend with team-membership resolution once
the org teams exist if strict "N-from-the-team" enforcement is required.

Env: GH_TOKEN, REPO (owner/name), PR_NUMBER.
"""

import json
import os
import subprocess
import sys

FOUNDATION_PREFIX = "foundation-wide/"
COUNT_FOUNDATION = 2
COUNT_DEFAULT = 1


def gh(path: str, paginate: bool = False):
    cmd = ["gh", "api", path]
    if paginate:
        cmd.append("--paginate")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"::error::gh api {path} failed: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(2)
    return json.loads(result.stdout)


def main() -> int:
    repo = os.environ["REPO"]
    pr = os.environ["PR_NUMBER"]

    files = gh(f"repos/{repo}/pulls/{pr}/files", paginate=True)
    paths = [f["filename"] for f in files]
    touches_foundation = any(p.startswith(FOUNDATION_PREFIX) for p in paths)
    required = COUNT_FOUNDATION if touches_foundation else COUNT_DEFAULT

    author = gh(f"repos/{repo}/pulls/{pr}")["user"]["login"]

    reviews = gh(f"repos/{repo}/pulls/{pr}/reviews", paginate=True)
    # Track the latest *decision* per user. COMMENTED reviews don't override an
    # existing approval (matches GitHub's own review-decision behavior).
    latest: dict[str, str] = {}
    for rv in reviews:
        state = rv["state"]
        if state in ("APPROVED", "CHANGES_REQUESTED", "DISMISSED"):
            latest[rv["user"]["login"]] = state

    approvers = sorted(u for u, s in latest.items() if s == "APPROVED" and u != author)
    count = len(approvers)

    tier = "foundation-wide" if touches_foundation else "group"
    print(f"PR #{pr} touches: {tier} → requires {required} approval(s)")
    print(f"Distinct approvers ({count}): {approvers or '—'}")

    if count < required:
        print(f"::error::This PR needs {required} approval(s) for a {tier} change, "
              f"but has {count}.")
        return 1
    print("✓ Approval count satisfied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

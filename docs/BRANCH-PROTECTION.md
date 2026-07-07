# Branch Protection & Enforcement Setup

`CONTRIBUTING.md` describes a two-tier approval policy and CI runs `validate` + `pr-evals`
on every PR. But policy + CI are only *advisory* until `main` is protected. This doc turns
the described process into an **enforced** one.

> **Prerequisite:** the repo must be in the **gatesfoundation** GitHub org (not a personal
> account) so `CODEOWNERS` can reference org teams. Create these teams first:
> `skills-working-group`, `idm-leads`, `global-health-leads`, `global-development-leads`,
> `policy-leads`, `finance-leads`, `it-leads`.

## What we want to enforce

1. No direct pushes to `main` — all changes via PR.
2. Required reviewers per path (routed by `.github/CODEOWNERS`).
3. CI must pass before merge: **`Validate skill structure and metadata`** (validate.yml)
   and **`Run evals for changed skills`** (pr-evals.yml).
4. Stale approvals dismissed when new commits are pushed.

## Apply it (gh CLI)

Replace `<ORG>` with `gatesfoundation`:

```bash
gh api -X PUT repos/<ORG>/gf-agent-skills/branches/main/protection --input - <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "Validate skill structure and metadata",
      "Run evals for changed skills",
      "Path-based approval count"
    ]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "require_code_owner_reviews": true,
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true
  },
  "restrictions": null
}
JSON
```

(The `contexts` strings must match the **job `name:` fields** in the workflows exactly.)

## The two-tier approval nuance (important)

GitHub branch protection has **one** `required_approving_review_count` per branch — it can't
say "2 for `foundation-wide/`, 1 for `groups/`." Options:

| Option | How | Trade-off |
|---|---|---|
| **A. Count = 1 + code-owner review** (recommended start) | Set count to 1; CODEOWNERS routes the right reviewer. Foundation-wide's 2nd approval is a documented Working-Group norm. | Simple; the 2nd foundation-wide approval isn't hard-enforced yet |
| **B. Count = 2 globally** | Every PR needs 2 approvals | Over-enforces group skills (they'd need 2, not 1) |
| **C. Custom approval-count check** (recommended for strict 2-vs-1) | Set count = 1 + code-owner review, and add the **`Path-based approval count`** check (`.github/workflows/approval-count.yml` + `scripts/check_approvals.py`) as a required status check. It reads the PR's changed paths and fails unless there are 2 approvals for `foundation-wide/`, 1 for `groups/`. | True path-specific counts; the check counts distinct approvers (relies on code-owner review for team membership — see the script's extension note) |

**Recommendation:** if the two-tier count is a convention, use **Option A** (count = 1 + code-owner
review). If it must be **hard-enforced**, use **Option C**: keep count = 1 in branch protection and
add the `Path-based approval count` check to `contexts` (already included above). The check supplies
the path-aware "2 for foundation-wide" rule that native branch protection can't.

## Solo-owner caveat

If the org has few reviewers, note you **cannot approve your own PR**. Keep `enforce_admins: false`
so an admin can merge in a pinch, and make sure the code-owner teams have members other than the
PR author.

## Verify

After applying, open a test PR that edits a skill and confirm:
- It cannot be merged without a code-owner approval.
- The `validate` and `pr-evals` checks appear as required.
- Direct `git push origin main` is rejected.

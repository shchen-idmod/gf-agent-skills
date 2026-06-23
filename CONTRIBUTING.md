# Contributing Skills

## Before you open a PR

Run these two commands from the repo root. Both must pass with no errors.

```bash
# 1. Check skill structure and metadata (free — no API calls)
python scripts/validate_skill.py

# 2. Run your skill's evals against Claude (requires ANTHROPIC_API_KEY)
python scripts/run_evals.py --plugin <plugin> --skill <your-skill-name>
```

PRs that fail either check will be blocked by CI.

---

## PR checklist

- [ ] `SKILL.md` exists with required frontmatter: `name`, `description`, `owner`, `version` — see [docs/SKILL_TEMPLATE.md](docs/SKILL_TEMPLATE.md)
- [ ] `SKILL.md` has `## Instructions`, `## Output Format`, and `## Limitations` sections
- [ ] `evals/evals.json` exists with at least 3 meaningful test cases
- [ ] All evals pass locally (`run_evals.py` exits 0)
- [ ] Skill validates locally (`validate_skill.py` exits 0)

---

## Writing evals

See [docs/EVALS.md](docs/EVALS.md) for the full schema reference and guidance on writing evals that test real behavior (not trivially-passing string checks).

Minimum: **3 cases per skill.**

---

## Approval requirements

| Tier | Where it lives | Approvals required |
|---|---|---|
| Foundation-wide | `foundation-wide/skills/` | 2 — from the Skills Working Group |
| Group | `groups/<your-group>/skills/` | 1 — from your team lead |

---

## Where does my skill go?

| Audience | Path |
|---|---|
| All GF staff | `foundation-wide/skills/` |
| Your team only | `groups/<your-group>/skills/` |

Valid group names: `idm`, `global-health`, `global-development`, `policy`, `finance`, `it`. Note, this can be extended

---

## Using skills in your own repo (Git Submodule)

If you want to use GF skills inside your own project repo rather than installing them via the marketplace, you can add this repo as a Git submodule.

**Add the submodule:**
```bash
git submodule add https://github.com/gatesfoundation/gf-agent-skills.git .claude/skills/gf-agent-skills
git commit -m "Add gf-agent-skills as submodule"
git push
```

**After cloning a repo that already has the submodule:**
```bash
git submodule update --init --recursive
```

**Reference only the skills you need in your repo's `CLAUDE.md`:**
```markdown
## Skills
- .claude/skills/gf-agent-skills/foundation-wide/skills/research/literature-review/SKILL.md
- .claude/skills/gf-agent-skills/groups/idm/skills/software-tools/python-code-reviewer/SKILL.md
```

**Keep skills up to date:**
```bash
git submodule update --remote --merge
git commit -m "Update gf-agent-skills to latest"
git push
```

> **Tip:** Automate updates via Dependabot by adding this to your repo's `.github/dependabot.yml`:
> ```yaml
> version: 2
> updates:
>   - package-ecosystem: "gitsubmodules"
>     directory: "/"
>     schedule:
>       interval: "weekly"
> ```

---

## Running evals

```bash
# One skill
python scripts/run_evals.py --plugin foundation-wide --skill literature-review

# All foundation-wide skills
python scripts/run_evals.py --plugin foundation-wide

# Everything
python scripts/run_evals.py

# Only skills changed on your branch (same filter CI uses)
python scripts/run_evals.py --changed-from origin/main

# Override with a custom fixture file (useful for PII / edge-case testing)
python scripts/run_evals.py --plugin idm --skill idm-pkg-install --fixture pii_test_cases.json

# Use real data from an env var and mask PII in the saved results
TEST_REAL_FIXTURES_PATH=/path/to/real.json \
  python scripts/run_evals.py --plugin idm --skill idm-pkg-install --real --mask-output --output results.json
```

`--fixture` and `--real` require `--plugin` and `--skill` (they apply to one skill at a time).
Fixture files are looked up first as an absolute path, then in `fixtures/synthetic/` and `fixtures/real/`.
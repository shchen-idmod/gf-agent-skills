# IDM Skills

Reusable Claude skills scoped to Institute for Disease Modeling (IDM) workflows — disease modeling, epidemiology research, and scientific software tools.

## Install

```
/plugin install idm-skills@bmgf-agent-skills
```

## Skills

| Skill | Category | Description |
|---|---|---|
| `disease-modeling-review` | Disease Modeling | Review and critique disease models (Starsim, EMOD, and others) for structure, parameterization, and calibration |
| `python-code-reviewer` | Software Tools | Review Python files for bugs, security issues, and code quality |
| `python-code-fixer` | Software Tools | Apply fixes identified by `python-code-reviewer` |
| `idm-pkg-install` | Software Tools | Install IDM packages from PyPI, GitHub, or local paths |

## Ownership

| Role | Contact |
|---|---|
| Group owner | bmgf-ai-skills@gatesfoundation.org |
| Reviewer / team lead | *(to be assigned)* |

## Contributing

1. Read the repo-level [CONTRIBUTING.md](../../CONTRIBUTING.md) first.
2. Add your skill under `skills/<category>/<skill-name>/` following the [skill folder template](../../docs/SKILL_FOLDER_TEMPLATE.md).
3. Include `SKILL.md` and `evals/evals.json` with at least 3 test cases — PRs without evals will not be merged.
4. Open a PR and request review from the IDM team lead.
5. One approval is required before merging group-scoped skills.

IDM-specific skills that prove stable and broadly useful may be nominated for promotion to `foundation-wide/` through the Skills Working Group.

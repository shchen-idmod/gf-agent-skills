# Skill Template

Copy the frontmatter and section headers below into your new skill's `SKILL.md` and fill in the placeholders.

---

```markdown
---
name: your-skill-name
description: Use when [specific triggering condition — start with "Use when"]
owner: your-team
version: 1.0.0
---

# Skill Title

## Instructions

[What the skill does and how the agent should behave. Be specific about actions, tone, and scope.]

## Output Format

[Describe the expected structure of responses: sections, length, format, examples.]

## Limitations

[What this skill does NOT do. Be explicit so users don't get surprised.]
```

---

## PR checklist before opening a pull request

- [ ] `SKILL.md` has all required frontmatter fields: `name`, `description`, `owner`, `version`
- [ ] `SKILL.md` has `## Instructions`, `## Output Format`, and `## Limitations` sections
- [ ] `<skill-name>/evals/evals.json` exists with at least 3 meaningful test cases (see [EVALS.md](EVALS.md))
- [ ] Evals pass locally: `python scripts/run_evals.py --plugin <plugin> --skill <skill-name>`
- [ ] Skill validates locally: `python scripts/deploy.py --plugin <plugin>`

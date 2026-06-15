# Plugin Template

A **plugin** is a collection of skills bundled together for a specific audience. Each plugin lives in its own directory with a `plugin.json` registry file.

---

## Folder structure

### Foundation-wide plugin

```
foundation-wide/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── <category>/
        └── <skill-name>/
            ├── SKILL.md
            └── evals/
                └── evals.json
```

Valid categories: `research`, `communications`, `operations`, `data`, `learning`

### Group plugin

```
groups/<your-group>/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── <skill-name>/
        ├── SKILL.md
        └── evals/
            └── evals.json
```

Valid group names: `idm`, `global-health`, `global-development`, `policy`, `finance`, `it`

---

## plugin.json

### Foundation-wide

```json
{
  "name": "foundation-wide-skills",
  "version": "1.0.0",
  "description": "Foundation-wide skills available to all GF staff.",
  "skills": [
    "./skills/research/your-skill-name"
  ]
}
```

### Group

```json
{
  "name": "your-group-skills",
  "version": "1.0.0",
  "description": "Skills for the [Your Group] team.",
  "skills": [
    "./skills/your-skill-name"
  ]
}
```

**Rules:**
- `name` must be unique across all plugins and use kebab-case
- `version` follows semver — bump the minor version when adding a skill, patch for fixes
- Each entry in `skills` is a path relative to the plugin root (the directory containing `.claude-plugin/`)
- Add a new entry to `skills` every time you add a skill; removing an entry unregisters the skill

---

## Adding a new skill to an existing plugin

1. Create the skill directory and files (see [SKILL_TEMPLATE.md](SKILL_TEMPLATE.md))
2. Add the path to `skills` in `plugin.json`
3. Bump `version` (minor bump)
4. Run validation: `python scripts/deploy.py --plugin <your-plugin>`

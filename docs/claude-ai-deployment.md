# Claude.ai Deployment Guide

Skills in this repo can be deployed to Claude.ai as ZIP uploads. This is separate from Claude Code — Claude.ai uses a UI-based upload flow rather than the marketplace.

---

## When to use this

| Deployment target | Method |
|---|---|
| Claude Code (desktop/IDE) | Marketplace install — see README |
| Claude.ai (browser) | ZIP upload — this guide |

---

## Step 1 — Package the skills

From the repo root, run:

```bash
python scripts/deploy.py --package --plugin foundation-wide
python scripts/deploy.py --package --plugin idm
```

This validates all skills first, then writes ZIPs to `dist/claude-ai/`:

```
dist/claude-ai/
├── literature-review.zip
├── grant-writing.zip
├── meeting-summarization.zip
├── pipeline-documentation.zip
└── ...
```

Each ZIP contains one skill folder (e.g. `literature-review/SKILL.md` and supporting files).

---

## Step 2 — Upload to Claude.ai

### Personal use

1. Go to [claude.ai](https://claude.ai) → **Settings** → **Customize** → **Skills**
2. Click **Upload skill**
3. Select the ZIP for the skill you want to install
4. Repeat for each skill

### Team or org-wide (Team / Enterprise plan)

1. Go to [claude.ai](https://claude.ai) → **Organization Settings** → **Skills**
2. Click **Upload skill**
3. Select the ZIP and upload
4. Toggle the skill **ON** to provision it to all org members

---

## Step 3 — Verify

After uploading, open a new Claude.ai conversation and type `/` — the skill should appear in the slash command list. Test it with a simple prompt to confirm it loaded correctly.

---

## Updating a skill

Claude.ai does not auto-update skills from the repo. When you merge a change to a skill:

1. Bump the `version` in the skill's `SKILL.md` frontmatter
2. Re-run `python scripts/deploy.py --package --plugin <plugin>`
3. Re-upload the ZIP in Claude.ai — it will replace the previous version

---

## Troubleshooting

**Skill doesn't appear after upload**
- Confirm the ZIP contains a `SKILL.md` at the top level of the skill folder
- Run `python scripts/deploy.py --plugin <plugin>` to validate before packaging

**Skill behaviour is wrong**
- Check the `## Instructions` section in `SKILL.md` — that is what Claude.ai loads
- Re-package and re-upload after any edits

**ZIP rejected by Claude.ai**
- ZIP must contain exactly one skill per file
- File size limit is enforced by Claude.ai — if a skill has large assets, check `dist/claude-ai/` file sizes

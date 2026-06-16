# GF Foundation Skills

A governed catalog of reusable AI skills for the Bill & Melinda Gates Foundation.

> **Compatible with:** Claude.ai · Claude Code · GitHub Copilot · Cursor · any tool supporting [Agent Skills](https://agentskills.io)

---

## Skill Catalog

### Foundation-Wide Skills
Available to all GF staff regardless of team or domain.

| Skill | Category | Owner |
|---|---|---|
| [literature-review](foundation-wide/skills/research/literature-review/) | Research | IDM |
| [grant-writing](foundation-wide/skills/communications/grant-writing/) | Communications | IDM |
| [meeting-summarization](foundation-wide/skills/operations/meeting-summarization/) | Operations | IDM |
| [pipeline-documentation](foundation-wide/skills/data/pipeline-documentation/) | Data | IDM |

### Group Skills

| Skill | Group | Category | Owner |
|---|---|---|---|
| [disease-modeling-review](groups/idm/skills/disease-modeling-review/) | IDM | Disease Modeling | IDM |
| [python-code-reviewer](groups/idm/skills/software-tools/python-code-reviewer/) | IDM | Software Tools | IDM |
| [python-code-fixer](groups/idm/skills/software-tools/python-code-fixer/) | IDM | Software Tools | IDM |
| [idm-pkg-install](groups/idm/skills/software-tools/idm-pkg-install/) | IDM | Software Tools | IDM |

---

## Where Does My Skill Go?

### Foundation-Wide (`foundation-wide/skills/<category>/`)
For skills useful to **all GF staff** regardless of team.

| Category | What belongs here |
|---|---|
| `research/` | Literature review, evidence synthesis, citation management |
| `communications/` | Grant writing, report drafting, stakeholder updates |
| `operations/` | Meeting summaries, project tracking, process documentation |
| `data/` | Pipeline docs, data dictionaries, analysis writeups |
| `learning/` | Onboarding guides, training materials, knowledge capture |

Requires **2 approvals** from the Skills Working Group.

### Group (`groups/<your-group>/skills/`)
For skills scoped to a specific GF team or program.

| Group | Team |
|---|---|
| `idm/` | Institute for Disease Modeling |
| `global-health/` | Global Health program |
| `global-development/` | Global Development program |
| `policy/` | Policy & Advocacy |
| `finance/` | Finance |
| `it/` | IT & Engineering |

Requires **1 approval** from your team lead.

---

## Deployment

### Claude Code (install via marketplace)
```bash
# Add this marketplace once
/plugin marketplace add gatesfoundation/gf-agent-skills

# Install by group
/plugin install foundation-wide-skills@gf-agent-skills
/plugin install idm-skills@gf-agent-skills
/plugin install global-health-skills@gf-agent-skills
```

### Claude.ai (upload via UI)
```bash
# Package skills as ZIPs
python scripts/deploy.py --package --plugin foundation-wide
python scripts/deploy.py --package --plugin idm
```
Then upload ZIPs at:
- **Personal:** `claude.ai → Settings → Customize → Skills → Upload skill`
- **Org-wide (Team/Enterprise):** `claude.ai → Organization Settings → Skills → Upload`

See [docs/claude-ai-deployment.md](docs/claude-ai-deployment.md) for the full guide including updates and troubleshooting.

---

## Contributing

```bash
# Validate all skills (default — no flags needed)
python scripts/deploy.py

# Validate a specific plugin or skill
python scripts/deploy.py --plugin foundation-wide
python scripts/deploy.py --plugin idm --skill disease-modeling-review
```

See [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/SKILL_TEMPLATE.md](docs/SKILL_TEMPLATE.md).

---

## Repository Structure

```
gf-agent-skills/
├── .claude-plugin/
│   └── marketplace.json              ← Claude Code marketplace registry
│
├── foundation-wide/                  ← Skills for all GF staff
│   ├── .claude-plugin/plugin.json
│   └── skills/
│       ├── research/
│       │   └── literature-review/
│       │       ├── SKILL.md
│       │       ├── evals/evals.json
│       │       └── scripts/          ← optional helper scripts
│       ├── communications/
│       │   └── grant-writing/
│       ├── operations/
│       │   └── meeting-summarization/
│       ├── data/
│       │   └── pipeline-documentation/
│       └── learning/                 ← empty, ready for contributions
│
├── groups/                           ← Team-scoped skills
│   ├── idm/
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/
│   │       ├── disease-modeling-review/
│   │       └── software-tools/
│   │           ├── python-code-reviewer/
│   │           ├── python-code-fixer/
│   │           └── idm-pkg-install/
│   ├── global-health/                ← empty, ready for contributions
│   ├── global-development/
│   ├── policy/
│   ├── finance/
│   └── it/
│
├── scripts/
│   ├── deploy.py                     ← validate or package for Claude.ai
│   └── validate_skill.py             ← also runs in CI on every PR
│
└── docs/
    ├── GOVERNANCE.md
    ├── SKILL_TEMPLATE.md
    └── claude-ai-deployment.md
```

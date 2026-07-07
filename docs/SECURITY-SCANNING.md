# Security Scanning

Every skill is scanned for security red flags before it can reach users. This implements the
foundation's requirement that "downloaded skills are vetted for security."

## The tool

We use [`cisco-ai-skill-scanner`](https://github.com/cisco-ai-defense/skill-scanner) — a
purpose-built scanner for Agent Skills. It detects red flags such as: data exfiltration,
credential/token requests, reading agent memory/identity files, network calls to raw IPs, silent
package installs, writing outside the workspace, obfuscated code, and browser-cookie access.

It has multiple engines:
- **Static analysis** (regex/AST) — fast, no key.
- **Behavioral dataflow** (`--use-behavioral`) — traces tainted data to sinks.
- **LLM semantic analysis** (optional) — needs `SKILL_SCANNER_LLM_API_KEY`.

## Two-tier model

| Tier | When | Engines | Gate |
|---|---|---|---|
| **Automated (CI)** | Every PR touching a skill | Static + behavioral | `security-scan.yml` — **fails on HIGH**, uploads SARIF to Code Scanning |
| **Deep review (human)** | Foundation-wide + anything the panel flags | + LLM semantic + manual read | Security/compliance reviewer on the Skills Working Group |

The CI tier is a fast, keyless gate that blocks obvious problems. The deep tier is part of the
human review for higher-tier skills (workstream owned with InfoSec).

## Run it locally (before opening a PR)

```bash
pip install cisco-ai-skill-scanner

# scan one skill
skill-scanner scan groups/idm/skills/software-tools/idm-pkg-install

# scan everything, like CI does
skill-scanner scan-all . --recursive --use-behavioral --fail-on-severity high

# optional LLM semantic pass
export SKILL_SCANNER_LLM_API_KEY=...   # and SKILL_SCANNER_LLM_MODEL
skill-scanner scan <path> --use-llm
```

Findings appear as inline PR annotations (via SARIF → GitHub Code Scanning) and in the Actions log.

## Where findings show up

The CI job uploads SARIF, so results appear under the repo's **Security → Code scanning** tab and
as inline comments on the PR diff.

## Extending with foundation-specific rules

The built-in rules already cover most of the common red flags. Add custom rules only for gaps
specific to us (e.g. references to internal data paths, GF-confidential markers). The scanner
supports custom local rule paths via its `custom-rules` interface — see the scanner's
`docs/custom-rules.md`. A starting set of agent-safety rules (agent-memory access, IP exfiltration,
browser-data theft) was prototyped in `skillhub/scanner/examples/vetter-rules/` and can be ported
if the built-in rules don't already cover them.

> Prefer built-in, maintained rules over hand-written regexes. Only add custom rules for genuine
> gaps, and keep them under version control with a comment explaining the threat each addresses.

## First-run checklist

- [ ] Confirm the SARIF output flag with `skill-scanner scan-all --help` (some versions use
      `--output <file>`, others write to stdout — adjust `security-scan.yml` accordingly).
- [ ] Confirm `--fail-on-severity` threshold matches policy (default `high`).
- [ ] Add **"Scan skills for security red flags"** to branch protection's required checks
      (see [BRANCH-PROTECTION.md](BRANCH-PROTECTION.md)).

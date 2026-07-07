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

## Custom foundation rules

The built-in rules cover most red flags. We add a small set of foundation-specific YARA rules in
`scanner/custom-yara/gf_agent_safety.yara`, loaded via `--custom-rules scanner/custom-yara` (see
the workflow). They cover three checks that are especially relevant to us and not in the built-in
set:

- **`vetter_agent_memory_theft`** — a skill reading agent memory/identity files (`MEMORY.md`,
  `.claude/memory`, `claude_desktop_config.json`, …). Claude-specific and high value.
- **`vetter_ip_exfiltration`** — network calls to raw IPs (bypasses DNS logging), excluding private ranges.
- **`vetter_browser_data_theft`** — access to browser cookies / saved-login / profile databases.

These were derived from the [skill-vetter](https://clawhub.ai/spclaudehome/skill-vetter) RED FLAGS.

### Why only YARA (not the regex signatures)

The CLI's `--custom-rules` flag loads **YARA** rules only; custom regex signatures use a separate
`--rule-packs` mechanism (packaged packs, not loose YAML). The remaining skill-vetter regex rules
(curl/wget, credential prompts, system-file writes, silent installs, base64/eval/exec, sudo,
obfuscation) overlap with the scanner's **built-in** signature + behavioral engines, so we rely on
those rather than maintaining our own regexes.

> Before adding more custom rules, confirm the built-in set doesn't already cover the gap (run the
> scanner on a test skill). Add YARA rules for genuine gaps only, each with a comment explaining the
> threat it addresses.

## First-run checklist

- [ ] Confirm the SARIF output flag with `skill-scanner scan-all --help` (some versions use
      `--output <file>`, others write to stdout — adjust `security-scan.yml` accordingly).
- [ ] Confirm `--fail-on-severity` threshold matches policy (default `high`).
- [ ] Add **"Scan skills for security red flags"** to branch protection's required checks
      (see [BRANCH-PROTECTION.md](BRANCH-PROTECTION.md)).

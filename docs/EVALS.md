# Skill Evals

Evaluation framework for testing Claude skills against synthetic and real fixtures.

---

## Quick start

```bash
# Install dependencies
pip install anthropic pyyaml

# Copy env template and fill in your API key
cp .env.example .env

# Run evals for a skill
python scripts/run_evals.py --plugin foundation-wide --skill literature-review

# Run with a custom fixture file
python scripts/run_evals.py --plugin idm --skill idm-pkg-install --fixture pii_test_cases.json

# Run with real data and mask PII in saved results
TEST_REAL_FIXTURES_PATH=/path/to/real.json \
  python scripts/run_evals.py --plugin idm --skill idm-pkg-install --real --mask-output --output results.json
```

---

## Handling sensitive data

| Data type | Where it lives | Committed? |
|---|---|---|
| Synthetic fixtures | `fixtures/synthetic/` | ✅ Yes |
| Real fixtures | `fixtures/real/` | ❌ No (.gitignored) |
| API keys / passwords | `.env` | ❌ No (.gitignored) |
| Real fixture path | `TEST_REAL_FIXTURES_PATH` env var | ❌ No |

### Key rules
- **Never** put real SSNs, DOBs, employer IDs, passwords, or API keys in fixture files
- **Always** use `SensitiveDataMasker` (from `scripts/utils.py`) before logging or writing results to disk
- **Always** load secrets via `EnvSecrets.require()`, never hardcode them
- Real fixtures are loaded from a local path set in an env var — the path itself never enters the repo

---

## evals.json Schema

Every skill directory must contain `evals/evals.json`. Two formats are accepted:

**Wrapped format** (recommended — adds metadata):
```json
{
  "skill": "<skill-name>",
  "version": "1.0.0",
  "evals": [ ...cases... ]
}
```

**Bare array format** (minimal):
```json
[ ...cases... ]
```

### Eval case fields

| Field | Required | Description |
|---|---|---|
| `id` | ✅ | Unique identifier, e.g. `grant-001`. Use `<skill-prefix>-NNN`. |
| `name` | ✅ | Short human-readable label shown in CI output. |
| `description` | — | Longer explanation of what this case tests and why. |
| `input` | ✅ | The user message sent to the skill. Plain string. |
| `rubric` | ✅ | Pass/fail criteria — see Rubric fields below. |

### Rubric fields

All fields are optional but at least one must be present to be meaningful.

| Field | Type | Behaviour |
|---|---|---|
| `must_include_one_of` | `string[]` | At least one string must appear in the response (case-insensitive). |
| `must_include` | `string[]` | Every string must appear in the response. |
| `must_include_all` | `string[]` | Alias for `must_include`. |
| `must_not_include` | `string[]` | None of these strings may appear. |
| `required_sections` | `string[]` | Alias for `must_include` — use for section headings. |
| `must_include_groups` | `string[][]` | List of groups — each group requires at least one match (independent checks). |
| `pass_condition` | `string` | Human-readable description of passing criteria (not machine-checked — shown in CI output only). |

### Example: 3 meaningful test cases

```json
{
  "skill": "grant-writing",
  "version": "1.0.0",
  "evals": [
    {
      "id": "grant-001",
      "name": "Asks clarifying questions for a vague request",
      "description": "Vague request — agent should ask for missing context, not produce output immediately.",
      "input": "Help me write a grant proposal.",
      "rubric": {
        "must_include_one_of": ["funder", "what is the", "could you share", "which organization"],
        "must_not_include": ["problem statement", "theory of change"],
        "pass_condition": "Agent asks at least one clarifying question before producing content"
      }
    },
    {
      "id": "grant-002",
      "name": "Produces all required sections for a complete brief",
      "description": "Fully-specified request — agent should produce a complete proposal with all required sections.",
      "input": "Write a grant proposal for a malaria vaccine trial in Kenya. Funder: Gates Foundation. Budget: $2M over 3 years. Target: children under 5.",
      "rubric": {
        "required_sections": ["Problem", "Approach", "Budget"],
        "must_include_groups": [
          ["Evaluation", "Monitoring", "M&E", "measure success"],
          ["Feasibility", "team capacity", "well-positioned"]
        ],
        "pass_condition": "Proposal contains Problem, Approach, Budget sections plus evaluation and feasibility content"
      }
    },
    {
      "id": "grant-003",
      "name": "Declines to write proposal outside scope",
      "description": "Request outside the skill's scope — agent should decline rather than attempt it.",
      "input": "Write a grant proposal for a commercial product launch.",
      "rubric": {
        "must_include_one_of": ["out of scope", "not able to", "not designed", "philanthropic", "nonprofit"],
        "pass_condition": "Agent declines or redirects — this skill is for philanthropic grants only"
      }
    }
  ]
}
```

### Writing meaningful evals

A good eval tests what an agent does **without** the skill's explicit guidance — the behaviour the skill exists to enforce.

**Weak (trivially passes):** `"must_include_one_of": ["the", "a", "is"]`

**Strong:** Tests the specific behaviour the skill teaches:
- Does the agent ask for missing context rather than hallucinating it?
- Does the agent flag out-of-scope requests rather than attempting them?
- Does the output include all required sections when given a complete brief?

---

## Shared utilities (`scripts/utils.py`)

| Class | Purpose |
|---|---|
| `SensitiveDataMasker` | Masks PII fields/patterns before logging or writing results |
| `SyntheticDataFactory` | Generates deterministic fake PII for test fixtures |
| `FixtureLoader` | Loads fixtures from `fixtures/synthetic/` or `fixtures/real/` |
| `EnvSecrets` | Reads secrets from env vars only — never from files |

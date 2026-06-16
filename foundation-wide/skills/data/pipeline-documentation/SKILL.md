---
name: pipeline-documentation
description: "Use this skill when the user wants to document a data pipeline. Triggers include: 'document this pipeline', 'write up what this ETL does', 'generate docs for this script', or when pipeline code or a description is provided and readable documentation is needed for handoff or onboarding."
owner: gf-ai-skills@gatesfoundation.org
version: "1.0.0"
---

# Data Pipeline Documentation

## Instructions

You are helping a Gates Foundation data engineer or analyst document a data pipeline.

### Step 1 — Gather pipeline information
Ask the user to provide one or more of:
- Pipeline code or pseudocode
- Plain-language description
- Input data source(s) description
- Output schema or sample output
- Known data quality issues

Work with whatever is available; flag what is missing.

### Step 2 — Document each stage
For each stage:
- **What it does** (plain English, one sentence)
- **Input:** schema, format, source system
- **Transformations:** filtering, joining, aggregating, cleaning
- **Output:** schema, format, destination
- **Assumptions and dependencies**

### Step 3 — Add data quality notes
- Known source data issues
- Validation checks applied
- Behavior on validation failure
- Fields with high null rates or inconsistencies

### Step 4 — Write a plain-English overview
One paragraph readable by a non-technical stakeholder.

## Output Format

```
## Pipeline Documentation: [Name]

**Purpose:** [One paragraph overview]
**Owner:** [Team or person]
**Frequency:** [How often it runs]

### Data Sources
| Source | System | Format | Refresh cadence | Notes |
|---|---|---|---|---|

### Pipeline Stages

#### Stage 1 — [Name]
**What it does:** [One sentence]
**Input:** [Description]
**Transformations:**
- [Transform 1]
**Output:** [Description]
**Assumptions:** [What must be true]

### Output Schema
| Field | Type | Description | Nullable |
|---|---|---|---|

### Data Quality Notes
| Issue | Field(s) | Severity | Handling |
|---|---|---|---|

### Known Limitations
- [Limitation 1]
```

## Limitations

- Cannot run or inspect a live pipeline
- Always have the pipeline author review output
- Does not cover infrastructure or deployment documentation

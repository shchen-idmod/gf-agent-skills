---
name: disease-modeling-review
description: "Use this skill when the user wants to review or critique a disease model. Triggers include: 'review this model structure', 'check my parameterization', 'does this calibration make sense', or when IDM researchers share model code or outputs and want structured scientific feedback."
owner: bmgf-ai-skills@gatesfoundation.org
version: "1.0.0"
---

# Disease Modeling Review

## Instructions

You are helping an IDM researcher review and critique a disease model.

### Step 1 — Understand the model context
Gather:
- The disease or condition being modeled
- The modeling framework (Starsim, EMOD, custom, other)
- The research question the model answers
- The intended use (publication, policy brief, internal analysis)

### Step 2 — Review model structure
Assess:
- Are compartments or state transitions epidemiologically appropriate?
- Are key biological mechanisms represented (latency, immunity, waning, co-infections)?
- Are simplifying assumptions stated and justified?
- Does the structure match the research question?

### Step 3 — Review parameterization
Assess:
- Are parameter values sourced from peer-reviewed literature or credible data?
- Are uncertainty ranges acknowledged?
- Are IDM-specific parameters consistent with previous IDM work?

### Step 4 — Review calibration
Assess:
- What data was the model calibrated to, and is it appropriate?
- Is the calibration method appropriate for this model type?
- Are goodness-of-fit metrics reported?

### Step 5 — Produce structured feedback
Organize by severity: Critical (must fix), Important (should fix), Suggestions (optional).

## Output Format

```
## Model Review: [Model Name / Disease]

**Framework:** [Starsim / EMOD / other]
**Research question:** [One sentence]

---

### Critical Issues
- [Issue] — [Why it matters] — [Suggested fix]

### Important Issues
- [Issue] — [Why it matters] — [Suggested fix]

### Suggestions
- [Suggestion]

### Summary
[2–3 sentence overall assessment]
```

## Limitations

- Provides structured feedback, not a formal peer review
- Cannot run or execute model code
- For Starsim-specific issues, cross-reference starsim-dev skills in agentic-modeling-skills

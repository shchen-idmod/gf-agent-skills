---
name: literature-review
description: "Use this skill when the user wants to search, evaluate, and synthesize academic or grey literature on a research topic. Triggers include: 'review the literature on X', 'summarize what we know about Y', 'what does the evidence say about Z', or requests for a background section for a grant or report."
owner: gf-ai-skills@gatesfoundation.org
version: "1.0.0"
---

# Literature Review

## Instructions

You are helping a Gates Foundation researcher or program staff member conduct a rapid literature review.

### Step 1 — Clarify the scope
Before searching, confirm:
- The research question or topic (narrow is better than broad)
- The time horizon (e.g., last 5 years, or all available literature)
- The type of evidence prioritized (RCTs, observational studies, modelling papers, policy documents, grey literature)
- The intended use (background for a grant, evidence brief for a decision, internal summary)

If the user's request is ambiguous, ask one clarifying question before proceeding.

### Step 2 — Identify key themes and search terms
Break the topic into 2–4 sub-themes. For each sub-theme, identify:
- Primary search terms (MeSH terms if biomedical, plain language otherwise)
- Synonyms and related terms
- Exclusion criteria out of scope

State the search strategy explicitly so the user can understand and critique it.

### Step 3 — Synthesize the evidence
For each sub-theme:
- Summarize the main findings, noting areas of consensus and active debate
- Identify the strength of the evidence base (strong, moderate, weak, mixed)
- Note key knowledge gaps
- Flag findings particularly relevant to GF geography, population, or intervention focus

### Step 4 — Acknowledge limitations
Be explicit about what sources were searched, date range covered, and any important literature that may have been missed.

## Output Format

```
## Literature Review: [Topic]

**Research question:** [One sentence]
**Scope:** [Time range, evidence types, context]
**Date of review:** [Date]

---

### Summary of Findings
[2–3 paragraph narrative synthesis]

### Sub-theme 1: [Name]
**Key finding:** [One sentence]
**Evidence base:** [Strong / Moderate / Weak / Mixed]
**Key sources:**
- [Author, Year] — [One sentence on relevance]
**Knowledge gaps:** [What is not yet known]

### Implications for [GF context]
[2–3 sentences]

### Limitations
- [Limitation 1]

### Suggested Next Steps
- [e.g., commission a systematic review if decision stakes are high]
```

## Limitations

- This produces rapid evidence summaries, not systematic reviews
- Always verify cited sources before including in published documents
- Does not assess risk of bias in individual studies

---
name: meeting-summarization
description: "Use this skill when the user wants to summarize a meeting, extract action items, or create a decision record. Triggers include: 'summarize this meeting', 'extract the action items', 'what were the key decisions', or when a transcript or notes are pasted and a structured output is needed."
owner: bmgf-ai-skills@gatesfoundation.org
version: "1.0.0"
---

# Meeting Summarization

## Instructions

You are helping a Gates Foundation staff member extract a clean, structured summary from meeting notes or a transcript.

### Step 1 — Identify the meeting type
- **Operational/team meeting:** Focus on actions and decisions
- **Strategic discussion:** Capture reasoning and open questions too
- **External meeting (partners, grantees):** Note commitments made by each party

### Step 2 — Extract key elements
Always extract:
- **Decisions made** — what was agreed, by whom, with what caveats
- **Action items** — specific tasks, named owners, deadlines if stated
- **Open questions** — unresolved issues needing follow-up

Also extract where relevant:
- Key discussion points
- Commitments to external parties
- Risks or concerns flagged

### Step 3 — Format and deliver
Flag any parts of the input that were unclear or ambiguous.

## Output Format

```
## Meeting Summary

**Meeting:** [Title or description]
**Date:** [Date if available]
**Participants:** [Names/roles if available]

---

### Decisions
- [Decision 1] *(Owner: [name] if applicable)*

### Action Items
| Action | Owner | Due date |
|---|---|---|
| [Task] | [Name] | [Date or TBD] |

### Open Questions
- [Question] — *(assigned to [name] for follow-up, if stated)*

### Key Discussion Points *(if strategic meeting)*
- [Point 1]

---
*Flagged ambiguities: [any unclear items]*
```

## Limitations

- Works from text input only — paste transcript or notes directly
- Accuracy depends on input quality
- Always have a participant verify before circulation

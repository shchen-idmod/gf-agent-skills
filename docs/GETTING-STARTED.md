# Getting Started with Foundation Skills for Claude Code

Foundation-approved Claude skills are published in this **`gf-agent-skills`** marketplace.
This guide shows you how to add them to Claude Code in about a minute.

> **Which Claude am I using?** These steps apply to **Claude Code** (the CLI, and the Code
> experience in the desktop/IDE app). The Claude.ai chat/Cowork web experience is managed
> separately — see [claude-ai-deployment.md](claude-ai-deployment.md).

---

## Prerequisites

- **Claude Code installed** ([install guide]() — link to the foundation's Claude Code setup page).
- **Plugins enabled for your account.** If the commands below return an error like
  *"plugins are not enabled,"* your account/group doesn't have the capability yet — request it
  via [access request link]().

---

## Step 1 — Add the marketplace

In Claude Code, run:

```
/plugin marketplace add gatesfoundation/gf-agent-skills
```

> Replace `gatesfoundation/gf-agent-skills` with the canonical repo location if different.

This registers the marketplace for **your** installation only (it doesn't affect anyone else).
Note the marketplace is referenced by its declared name, **`gf-agent-skills`**, in the
install commands below.

## Step 2 — Install the plugins for your group

Everyone should install the foundation-wide plugin. Then add your group's plugin if it's available.

```
/plugin install foundation-wide-skills@gf-agent-skills
```

**Available now:**

| Plugin | What's in it | Command |
|---|---|---|
| **Foundation-wide** (all staff) | grant-writing, pipeline-documentation, meeting-summarization, literature-review | `/plugin install foundation-wide-skills@gf-agent-skills` |
| **IDM** (disease modeling, epi) | disease-modeling-review, idm-pkg-install, python-code-fixer, python-code-reviewer | `/plugin install idm-skills@gf-agent-skills` |

**Coming soon** (group plugins being populated): Global Health, Global Development, Policy, Finance,
IT. Want to seed your group's plugin? See "Requesting a new skill" below.

## Step 3 — Verify

```
/plugin
```

You should see the plugins you installed listed as enabled. Their skills are now available —
Claude will use them automatically when relevant (e.g., ask about installing an IDM package and
the `idm-pkg-install` skill kicks in).

---

## Keeping skills up to date

When new skills are approved and published, refresh your local copy:

```
/plugin marketplace update gf-agent-skills
```

---

## Requesting a new skill (or reporting a problem)

Have a skill idea, or want to contribute one your team built?

- **Request / propose a skill:** [open an issue on gf-agent-skills]() or [intake form]().
- All contributions go through review (security + quality sign-off) before publishing — see
  [CONTRIBUTING.md](../CONTRIBUTING.md).
- Found a bug in a skill? File an issue with the skill name and what went wrong.

---

## FAQ

**Q: Do other people see the plugins I install?**
No. Adding a marketplace/plugin is local to your machine. A foundation-wide automated rollout is
coming; for now each person adds it themselves using this guide.

**Q: Can I use these in the Claude.ai web app?**
Not through this flow — the web experience is centrally managed. This guide is for Claude Code.
See [claude-ai-deployment.md](claude-ai-deployment.md).

**Q: The commands don't work / I get a permissions error.**
Your account likely doesn't have plugins enabled yet. Request access via [link]().

**Q: Can I add my own or other marketplaces?**
Today, yes (Claude Code is open). As the governed rollout matures, general staff will be limited to
the approved marketplace; builders will retain flexibility. Prefer the approved marketplace so your
skills are the reviewed, supported ones.

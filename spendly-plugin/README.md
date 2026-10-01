# spendly-plugin

A Claude Code plugin for **Spendly** — the Flask + SQLite personal expense tracker built with a spec-driven workflow.

## What's inside

```
spendly-plugin/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── expense-entry/SKILL.md      # conventions for app.py routes + database/ layer
│   ├── spec-driven-dev/SKILL.md    # the .claude/specs/ workflow this repo uses
│   └── budget-report/SKILL.md      # conventions for aggregate/report views
├── hooks/
│   ├── hooks.json                  # wires production-guard.js into PreToolUse
│   └── production-guard.js         # blocks direct writes/deletes to spendly.db & spendly-backup.db
└── commands/
    ├── new-spec/command.md         # /spendly-plugin:new-spec — scaffold a new feature spec
    └── db-check/command.md         # /spendly-plugin:db-check — read-only DB sanity check
```

## Install (local development)

From inside your Spendly repo:

```bash
# option 1: load for just this session
claude --plugin-dir /path/to/spendly-plugin

# option 2: install from a local marketplace
claude plugin marketplace add /path/to/spendly-plugin
claude plugin install spendly-plugin
```

## Notes

- This assumes the repo layout from your GitHub screenshot: `app.py` (single-file Flask routes), `database/` (query/schema layer), `templates/`, `static/`, `tests/` + `pytest.ini`, and `spendly.db` / `spendly-backup.db` at the repo root.
- You already have a project-level `.claude/SKILL.md` — the `spec-driven-dev` skill here explicitly defers to it, so the two shouldn't conflict.
- The guard hook fails open (never blocks) if it can't parse the hook input, so it won't brick your session — but that also means it's a safety net, not a substitute for care around the live `.db` file.

## Next steps to tighten this further

Paste in (or let me read) any of:
- `app.py` — so route naming/conventions in `expense-entry` match reality
- `database/` contents — so the "helper vs inline SQL" guidance points at real function names
- an existing file from `.claude/specs/` (if one exists) — so `new-spec` matches your actual template

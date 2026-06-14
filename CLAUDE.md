# CLAUDE.md

This project's guidance for Claude Code (and any AI agent) lives in **[AGENTS.md](./AGENTS.md)** —
read it first.

Quick reminders (the rest is in AGENTS.md):

- All tax math goes through `bd-income-tax/scripts/tax_calc.py` — never hand-calculate.
- Run `python3 bd-income-tax/scripts/tax_calc.py --selftest` before committing.
- Keep `plugin.json`, `.claude-plugin/marketplace.json`, and `CHANGELOG.md` versions in sync.
- Conventional Commits; signed, sole-author commits with no AI co-author trailer.

For the skill's runtime behavior (how answers are presented), see
[`bd-income-tax/SKILL.md`](./bd-income-tax/SKILL.md).

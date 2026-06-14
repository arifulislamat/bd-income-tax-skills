# bd-income-tax-skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Agent Skill](https://img.shields.io/badge/Agent-Skill-blue.svg)](https://agentskills.io)
[![Built with Claude](https://img.shields.io/badge/Built%20with-Claude-d97757.svg)](https://claude.com/claude-code)

Agent Skill for **Bangladesh individual (personal) income tax**. It lets any compatible AI
agent (Claude, Codex, Gemini CLI, etc.) accurately answer Bangladesh personal income-tax
questions and compute tax for a given assessment year — slabs, tax-free thresholds, salary
exemption, the Section 78 investment rebate, minimum tax, net-wealth surcharge, TDS credit,
filing/PSR rules, Tax Day, and penalties.

The skill lives in [`skills/bd-income-tax/`](./skills/bd-income-tax). Authored to the open
[Agent Skills](https://agentskills.io) standard, so the same `SKILL.md` runs unmodified
across the tools that adopted it.

## What it does

- **Year-aware.** Bangladesh income year is 1 Jul – 30 Jun → the *following* assessment year.
  Primary year **AY 2026-27**; also supports **AY 2025-26** for late/prior returns. Every
  answer states the assessment year and governing law.
- **Deterministic math.** All arithmetic runs through
  [`skills/bd-income-tax/scripts/tax_calc.py`](./skills/bd-income-tax/scripts/tax_calc.py) — standard
  library only, **no network calls**, no model arithmetic.
- **Sourced.** Every rate/threshold is tagged with its source in
  [`references/sources.md`](./skills/bd-income-tax/references/sources.md).

## Assessment-year caveat

The FY 2026-27 measures were placed as a **Finance Bill** on 11 Jun 2026 and are expected to
become the **Finance Act 2026** (effective 1 Jul 2026). Until gazetted, treat AY 2026-27
figures as provisional. A few edge-case figures (DPS cap, agriculture deemed-cost %,
solely-agricultural exemption, delay-interest rate) are marked **⚠️ unverified** in the
references and are deliberately **not** used by the calculator.

## Quick start (calculator)

```bash
python3 skills/bd-income-tax/scripts/tax_calc.py --selftest        # runs the canonical test cases
python3 skills/bd-income-tax/scripts/tax_calc.py --year 2026-27 --category general --salary 800000
```

Canonical results the self-test asserts: **15,833 / 70,070 / 7,500 / 49,500**.

## Install

- **skills.sh (any agent — Claude, Codex, Cursor, …):**
  ```
  npx skills add arifulislamat/bd-income-tax-skills
  ```
- **Claude Code plugin marketplace:**
  ```
  /plugin marketplace add arifulislamat/bd-income-tax-skills
  /plugin install bd-income-tax@bd-income-tax-skills
  ```
- **Claude.ai / desktop apps:** download **`bd-income-tax.zip`** from the
  [latest release](https://github.com/arifulislamat/bd-income-tax-skills/releases/latest) and
  upload it under Settings → Capabilities → Skills. The archive is the skill folder itself
  (top-level `bd-income-tax/` with `SKILL.md` inside), so no manual zipping is needed — do
  **not** use GitHub's "Source code" zip, which wraps everything in the repo root.
- **OpenAI Codex CLI:** place `skills/bd-income-tax/` under `~/.agents/skills/`.
- **Gemini CLI / Antigravity:** place under `~/.gemini/...` (CLI) or `.agent/skills/`.
- **Clone & copy:** `git clone` this repo and copy `skills/bd-income-tax/` into your agent's skills directory.

The consumer ChatGPT and Gemini apps do not load `SKILL.md`; a GPT/Gem front-end would need
to link out to this repo for the full dataset.

## Updating

When a newer release is published, update in Claude Code by running these **one at a time**
(slash commands only run when entered on their own, not pasted together):

```
/plugin marketplace update bd-income-tax-skills
/plugin update bd-income-tax@bd-income-tax-skills
```

The first refreshes the marketplace from GitHub; the second installs the new version. Confirm
the version under `/plugin` → **Marketplaces**, or against the [CHANGELOG](./CHANGELOG.md).

For the **desktop / Claude.ai** route, re-download the latest `bd-income-tax.zip` from the
[latest release](https://github.com/arifulislamat/bd-income-tax-skills/releases/latest) and
re-upload it under Settings → Capabilities → Skills.

## How this was built

This skill was authored with **AI assistance (Claude Code)**. Every rate, threshold, and
figure is grounded in the cited sources in
[`references/sources.md`](./skills/bd-income-tax/references/sources.md) and verified by the
deterministic calculator's self-tests — not produced free-hand. Corrections and source
updates are welcome; see [CONTRIBUTING.md](./CONTRIBUTING.md).

## Disclaimer

Informational only; **not professional tax advice.** Verify against the current gazetted
**Finance Act 2026** and NBR circulars (`nbr.gov.bd`). Individual/personal tax scope only —
not corporate tax or VAT.

## License

[MIT](./LICENSE).

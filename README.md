# bd-income-tax-skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Agent Skill](https://img.shields.io/badge/Agent-Skill-blue.svg)](https://agentskills.io)
[![Built with Claude](https://img.shields.io/badge/Built%20with-Claude-d97757.svg)](https://claude.com/claude-code)

Agent Skill for **Bangladesh individual (personal) income tax**. It lets any compatible AI
agent (Claude, Codex, Gemini CLI, etc.) accurately answer Bangladesh personal income-tax
questions, compute tax for a given assessment year, and help fill the online return on the
NBR e-Return site: slabs, tax-free thresholds, salary exemption, the Section 78 investment
rebate, minimum tax, net-wealth surcharge, source-tax credits, filing windows, and PSR rules.

The skill lives in [`skills/bd-income-tax/`](./skills/bd-income-tax). Authored to the open
[Agent Skills](https://agentskills.io) standard, so the same `SKILL.md` runs unmodified
across the tools that adopted it.

## What it does

- **Year-aware.** Bangladesh income year is 1 Jul to 30 Jun → the *following* assessment year.
  Primary year **AY 2026-27**; also **AY 2025-26** (late/prior returns) and the four years the
  Finance Act 2026 legislated in advance, **AY 2027-28 to AY 2030-31** (flagged as estimates).
  Every answer states the assessment year and governing law.
- **Aligned with the gazetted law.** AY 2026-27 figures are checked against the Finance Act
  2026 (Act No. 96 of 2026) and the NBR Income Tax Guide 2026-27; the self-test reproduces the
  guide's own worked examples.
- **Filing windows.** Models the AY 2026-27 timing rules that replaced Tax Day: the early-filing
  incentive and the additional tax for late windows (`--filing-date`).
- **Credits done right.** Source tax is refundable; **vehicle advance tax** (Section 153) is a
  *non-refundable* credit against income tax only, so "a car reduces my tax" is answered
  correctly. Also models the **gratuity exemption**, flat-rate dividends and gold gains, and
  the turnover-tax check for businesses.
- **Guided e-Return filing.** With a browser tool (Claude in Chrome, or the Claude desktop
  app's built-in browser) the skill fills the return on `etaxnbr.gov.bd` screen by screen from
  a confirmed filing sheet, and cross-checks the site's tax against the calculator. You sign in,
  pay, and press the final submit yourself. See
  [`references/e-return-browser.md`](./skills/bd-income-tax/references/e-return-browser.md).
- **Deterministic math.** All arithmetic runs through
  [`skills/bd-income-tax/scripts/tax_calc.py`](./skills/bd-income-tax/scripts/tax_calc.py):
  standard library only, **no network calls**, no model arithmetic.
- **Sourced.** Every rate/threshold is tagged with its source in
  [`references/sources.md`](./skills/bd-income-tax/references/sources.md).

## What changed with the Finance Act 2026 (AY 2026-27)

| Item | AY 2025-26 | AY 2026-27 |
|---|---|---|
| General tax-free threshold | 350,000 | 400,000 |
| Women / age 65+ | 400,000 | 450,000 |
| Third-gender / disability | 475,000 | 525,000 |
| War-wounded freedom fighters (and July fighters from 2026-27) | 500,000 | 550,000 |
| First taxable slab | 5% | 10% |
| Investment rebate | lowest of 3% income, 15% investment, 1,000,000 | lowest of 3% income, **10%** investment, **750,000** |
| Minimum tax | 5,000 / 4,000 / 3,000 by area | 5,000 flat (1,000 new taxpayer) |
| Deadline | Tax Day, late filing lost the rebate | Filing windows: 5% off by 30 Sep, extra tax from January |
| Dividends | slab rates | 15% flat |

A few edge-case figures remain **⚠️ unverified** in the references, and the calculator's
stated assumptions are listed in `SKILL.md`. Confirm those against the official text.

## Quick start (calculator)

```bash
python3 skills/bd-income-tax/scripts/tax_calc.py --selftest        # runs the canonical test cases
python3 skills/bd-income-tax/scripts/tax_calc.py --year 2026-27 --category general --salary 800000
python3 skills/bd-income-tax/scripts/tax_calc.py --salary 1260000 --investment 270000 --filing-date 2026-09-15
python3 tools/check_repo.py                                        # versions, SKILL.md, evals vs calculator
```

## Filing your return with a browser tool

1. Install the skill (below) in an app that has a browser tool: Claude Code with the
   **Claude in Chrome** extension (`claude --chrome`), or the **Claude desktop app** with its
   built-in browser.
2. Ask, for example: *"Help me file my Bangladesh income tax return on etaxnbr.gov.bd."*
3. The skill collects your figures, runs the calculator, and shows a filing sheet to confirm.
4. You sign in to the site yourself (TIN, password, OTP). The skill then fills each screen and
   reads the values back to you.
5. You make the payment and press **Submit Return** yourself.

The skill never types your password or OTP, never pays, and never presses the final submit.
A skill can instruct Claude to use a browser tool but cannot switch one on: if no browser tool
is available, or the app blocks the site, the skill falls back to a step-by-step walkthrough
that you follow by hand.

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
